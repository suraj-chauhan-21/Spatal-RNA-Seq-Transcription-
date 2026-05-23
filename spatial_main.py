"""
Spatial Transcriptomics Analysis Pipeline
Main module for coordinating all analysis steps
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
import anndata as ad
import scanpy as sc
import squidpy as sq
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpatialAnalysisPipeline:
    """
    Main class for spatial transcriptomics analysis pipeline
    
    Parameters
    ----------
    config_path : str
        Path to configuration YAML file
    output_dir : str
        Output directory for results
    verbose : bool
        If True, print detailed progress information
    
    Attributes
    ----------
    adata : anndata.AnnData
        Main annotated data object
    config : dict
        Configuration parameters
    results : dict
        Storage for analysis results
    
    Examples
    --------
    >>> pipeline = SpatialAnalysisPipeline('config.yaml', 'results/')
    >>> pipeline.load_data('data/sample.h5ad')
    >>> pipeline.run_full_pipeline()
    """
    
    def __init__(
        self,
        config_path: str,
        output_dir: str = 'results/',
        verbose: bool = True
    ):
        """Initialize the pipeline"""
        
        self.config_path = Path(config_path)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.adata = None
        self.config = None
        self.results = {}
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_config()
        
        logger.info(f"Spatial Analysis Pipeline initialized")
        logger.info(f"Configuration: {self.config_path}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def load_data(self, data_path: str, platform: Optional[str] = None) -> None:
        """
        Load spatial data from various formats
        
        Parameters
        ----------
        data_path : str
            Path to data file or directory
        platform : str, optional
            Data platform ('merfish', 'visium', 'slideseq', 'h5ad')
        """
        logger.info(f"Loading data from {data_path}")
        
        data_path = Path(data_path)
        platform = platform or self.config.get('data', {}).get('platform', 'h5ad')
        
        try:
            if platform == 'h5ad':
                self.adata = ad.read_h5ad(data_path)
            elif platform == 'visium':
                self.adata = sq.read.visium(data_path)
            elif platform == 'merfish':
                self.adata = sq.read.merfish(data_path)
            elif platform == 'slideseq':
                self.adata = sq.read.slideseq(data_path)
            else:
                raise ValueError(f"Unknown platform: {platform}")
            
            logger.info(f"Data loaded: {self.adata.n_obs} cells × {self.adata.n_vars} genes")
            logger.info(f"Spatial coordinates shape: {self.adata.obsm['spatial'].shape}")
            
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def quality_control(self) -> None:
        """Run quality control on spatial data"""
        logger.info("Starting quality control...")
        
        if self.adata is None:
            raise ValueError("No data loaded. Please load data first.")
        
        qc_params = self.config.get('qc', {})
        
        try:
            # Calculate QC metrics
            sc.pp.calculate_qc_metrics(self.adata, inplace=True)
            
            # Add spatial-specific metrics
            sq.pp.spatial_neighbors(self.adata, radius=100)
            sq.pp.distogram(self.adata)
            
            # Filter based on thresholds
            min_counts = qc_params.get('min_counts', 100)
            min_genes = qc_params.get('min_genes', 50)
            max_mt_pct = qc_params.get('max_mt_pct', 20)
            
            n_before = self.adata.n_obs
            
            # Basic filtering
            sc.pp.filter_cells(self.adata, min_counts=min_counts)
            sc.pp.filter_cells(self.adata, min_genes=min_genes)
            sc.pp.filter_genes(self.adata, min_cells=1)
            
            # Mitochondrial filtering (if applicable)
            if max_mt_pct < 100:
                mito_genes = self.adata.var_names.str.startswith('MT-')
                if mito_genes.any():
                    self.adata.obs['pct_mito'] = (
                        self.adata[:, mito_genes].X.sum(axis=1) /
                        self.adata.X.sum(axis=1)
                    )
                    self.adata = self.adata[
                        self.adata.obs['pct_mito'] < max_mt_pct/100
                    ]
            
            n_after = self.adata.n_obs
            logger.info(f"QC filtering: {n_before} → {n_after} cells")
            
            # Store QC results
            self.results['qc'] = {
                'n_cells_before': n_before,
                'n_cells_after': n_after,
                'cells_removed': n_before - n_after
            }
            
        except Exception as e:
            logger.error(f"QC failed: {e}")
            raise
    
    def normalize(self) -> None:
        """Normalize expression data"""
        logger.info("Normalizing data...")
        
        if self.adata is None:
            raise ValueError("No data loaded.")
        
        try:
            # Log normalization
            sc.pp.normalize_total(self.adata, inplace=True)
            sc.pp.log1p(self.adata)
            
            logger.info("Data normalized (log-total)")
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}")
            raise
    
    def highly_variable_genes(self) -> None:
        """Select highly variable genes"""
        logger.info("Selecting highly variable genes...")
        
        hvg_params = self.config.get('hvg', {})
        n_top_genes = hvg_params.get('n_top_genes', 2000)
        
        try:
            sc.pp.highly_variable_genes(
                self.adata,
                n_top_genes=n_top_genes,
                inplace=True
            )
            
            logger.info(f"Selected {self.adata.var['highly_variable'].sum()} HVGs")
            
        except Exception as e:
            logger.error(f"HVG selection failed: {e}")
            raise
    
    def dimensionality_reduction(self) -> None:
        """Perform PCA and UMAP"""
        logger.info("Performing dimensionality reduction...")
        
        dr_params = self.config.get('dimensionality_reduction', {})
        n_pcs = dr_params.get('n_pcs', 20)
        
        try:
            # PCA
            sc.tl.pca(self.adata, n_comps=n_pcs)
            logger.info(f"PCA computed ({n_pcs} components)")
            
            # UMAP
            sc.pp.neighbors(self.adata, n_pcs=n_pcs)
            sc.tl.umap(self.adata)
            logger.info("UMAP computed")
            
        except Exception as e:
            logger.error(f"Dimensionality reduction failed: {e}")
            raise
    
    def clustering(self) -> None:
        """Perform spatial clustering"""
        logger.info("Clustering cells...")
        
        cluster_params = self.config.get('clustering', {})
        resolution = cluster_params.get('resolution', 0.5)
        use_spatial = cluster_params.get('use_spatial', True)
        
        try:
            if use_spatial:
                # Spatial clustering using neighbors
                sq.gr.spatial_neighbors(self.adata)
                sc.tl.leiden(self.adata, resolution=resolution)
                logger.info(f"Spatial clustering (Leiden, resolution={resolution})")
            else:
                # Standard clustering
                sc.tl.leiden(self.adata, resolution=resolution)
                logger.info(f"Clustering (Leiden, resolution={resolution})")
            
            n_clusters = len(self.adata.obs['leiden'].cat.categories)
            logger.info(f"Found {n_clusters} clusters")
            
            self.results['clustering'] = {'n_clusters': n_clusters}
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            raise
    
    def neighborhood_analysis(self) -> None:
        """Analyze spatial neighborhoods"""
        logger.info("Analyzing neighborhood...")
        
        try:
            # Spatial neighbors if not already computed
            if 'spatial_neighbors' not in self.adata.obsp:
                sq.gr.spatial_neighbors(self.adata)
            
            # Neighborhood enrichment
            sq.gr.nhood_enrichment(self.adata, cluster_key='leiden')
            
            logger.info("Neighborhood analysis completed")
            
        except Exception as e:
            logger.error(f"Neighborhood analysis failed: {e}")
            raise
    
    def run_full_pipeline(self) -> None:
        """Run the complete analysis pipeline"""
        logger.info("=" * 60)
        logger.info("STARTING FULL PIPELINE")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Sequential pipeline steps
            self.quality_control()
            self.normalize()
            self.highly_variable_genes()
            self.dimensionality_reduction()
            self.clustering()
            self.neighborhood_analysis()
            
            # Save processed data
            output_path = self.output_dir / 'processed_adata.h5ad'
            self.adata.write_h5ad(output_path)
            logger.info(f"Processed data saved to {output_path}")
            
            # Generate report
            self.generate_report()
            
            elapsed = datetime.now() - start_time
            logger.info("=" * 60)
            logger.info(f"PIPELINE COMPLETED in {elapsed}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise
    
    def generate_report(self) -> None:
        """Generate HTML analysis report"""
        logger.info("Generating analysis report...")
        
        try:
            report_dir = self.output_dir / 'report'
            report_dir.mkdir(exist_ok=True)
            
            # Create summary statistics
            summary = f"""
            <html>
            <head>
                <title>Spatial Transcriptomics Analysis Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #4CAF50; color: white; }}
                </style>
            </head>
            <body>
                <h1>Spatial Transcriptomics Analysis Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Dataset Summary</h2>
                <table>
                    <tr><th>Metric</th><th>Value</th></tr>
                    <tr><td>Number of Cells</td><td>{self.adata.n_obs}</td></tr>
                    <tr><td>Number of Genes</td><td>{self.adata.n_vars}</td></tr>
                    <tr><td>Spatial Coordinates</td><td>{self.adata.obsm['spatial'].shape}</td></tr>
                </table>
                
                <h2>Analysis Results</h2>
                <h3>Quality Control</h3>
                <p>Cells removed: {self.results.get('qc', {}).get('cells_removed', 'N/A')}</p>
                
                <h3>Clustering</h3>
                <p>Number of clusters: {self.results.get('clustering', {}).get('n_clusters', 'N/A')}</p>
                
            </body>
            </html>
            """
            
            report_path = report_dir / 'index.html'
            with open(report_path, 'w') as f:
                f.write(summary)
            
            logger.info(f"Report generated at {report_path}")
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")


if __name__ == '__main__':
    # Example usage
    pipeline = SpatialAnalysisPipeline(
        config_path='config/default_config.yaml',
        output_dir='results/'
    )
    
    # Load data and run pipeline
    # pipeline.load_data('data/sample.h5ad')
    # pipeline.run_full_pipeline()
