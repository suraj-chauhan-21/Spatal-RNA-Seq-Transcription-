#!/usr/bin/env python
"""
Example script for analyzing MERFISH spatial transcriptomics data
Uses the Squidpy and Scanpy ecosystem
"""

import sys
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scanpy as sc
import squidpy as sq
import anndata as ad

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from spatial_main import SpatialAnalysisPipeline
from spatial_visualization import SpatialVisualizer


def load_example_merfish_data():
    """Load example MERFISH dataset"""
    logger.info("Loading example MERFISH dataset...")
    
    try:
        # Load from squidpy datasets
        adata = sq.datasets.merfish()
        logger.info(f"Data loaded: {adata.n_obs} cells × {adata.n_vars} genes")
        
        # Check spatial coordinates
        if 'spatial' not in adata.obsm:
            logger.warning("No spatial coordinates found")
        else:
            logger.info(f"Spatial coordinates shape: {adata.obsm['spatial'].shape}")
        
        return adata
        
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        raise


def basic_analysis(adata: ad.AnnData, output_dir: str = 'results/merfish/'):
    """Perform basic spatial analysis"""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting basic analysis...")
    
    # 1. Quality Control
    logger.info("1. Quality Control")
    sc.pp.calculate_qc_metrics(adata, inplace=True)
    
    # Spatial QC
    sq.pp.spatial_neighbors(adata, radius=100)
    
    # 2. Normalization
    logger.info("2. Normalization")
    sc.pp.normalize_total(adata, inplace=True)
    sc.pp.log1p(adata)
    
    # 3. Highly Variable Genes
    logger.info("3. Highly Variable Genes")
    sc.pp.highly_variable_genes(adata, n_top_genes=2000, inplace=True)
    
    # 4. PCA
    logger.info("4. PCA")
    sc.tl.pca(adata, n_comps=20)
    
    # 5. Neighbors and UMAP
    logger.info("5. UMAP")
    sc.pp.neighbors(adata, n_pcs=20)
    sc.tl.umap(adata)
    
    # 6. Clustering (spatial)
    logger.info("6. Spatial Clustering")
    sq.gr.spatial_neighbors(adata, n_neighbors=6)
    sc.tl.leiden(adata, resolution=0.5)
    
    # 7. Neighborhood enrichment
    logger.info("7. Neighborhood Analysis")
    sq.gr.nhood_enrichment(adata, cluster_key='leiden')
    
    # Save processed data
    adata.write_h5ad(output_dir / 'processed_adata.h5ad')
    logger.info(f"Processed data saved to {output_dir / 'processed_adata.h5ad'}")
    
    return adata


def create_visualizations(
    adata: ad.AnnData,
    output_dir: str = 'results/merfish/figures/'
):
    """Create comprehensive visualizations"""
    
    logger.info("Creating visualizations...")
    
    viz = SpatialVisualizer(
        adata,
        output_dir=output_dir,
        figsize=(10, 10),
        dpi=150,
        format='pdf'
    )
    
    # 1. Spatial cluster map
    logger.info("  - Spatial cluster map")
    viz.cluster_map(
        cluster_key='leiden',
        size=20,
        save_name='01_spatial_clusters'
    )
    
    # 2. Gene expression maps for top genes
    logger.info("  - Gene expression maps")
    top_genes = adata.var_names[:5]
    for gene in top_genes:
        viz.gene_expression_map(
            gene,
            size=20,
            save_name=f'02_gene_{gene}'
        )
    
    # 3. Multi-gene panel
    logger.info("  - Multi-gene panel")
    viz.multi_gene_spatial(
        list(top_genes),
        n_cols=2,
        size=15,
        save_name='03_multi_genes'
    )
    
    # 4. UMAP colored by cluster
    logger.info("  - UMAP")
    sc.pl.umap(
        adata,
        color='leiden',
        save=f'{output_dir}/04_umap_clusters.pdf',
        show=False
    )
    
    # 5. Spatial QC
    logger.info("  - Spatial QC")
    viz.spatial_scatter(
        color='n_counts',
        size=20,
        save_name='05_spatial_qc_counts'
    )
    
    logger.info("Visualizations complete")


def generate_statistics(
    adata: ad.AnnData,
    output_dir: str = 'results/merfish/tables/'
) -> pd.DataFrame:
    """Generate summary statistics"""
    
    logger.info("Generating statistics...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Cluster statistics
    cluster_stats = pd.DataFrame({
        'Cluster': adata.obs['leiden'].cat.categories,
        'n_cells': adata.obs['leiden'].value_counts().sort_index().values,
        'mean_counts': [adata[adata.obs['leiden'] == c, :].X.mean() for c in adata.obs['leiden'].cat.categories]
    })
    
    # Save statistics
    cluster_stats.to_csv(output_dir / 'cluster_statistics.csv', index=False)
    logger.info(f"Statistics saved to {output_dir / 'cluster_statistics.csv'}")
    
    # Print summary
    logger.info("\nCluster Statistics:")
    logger.info(cluster_stats.to_string())
    
    return cluster_stats


def main():
    """Main analysis pipeline"""
    
    logger.info("=" * 70)
    logger.info("MERFISH SPATIAL TRANSCRIPTOMICS ANALYSIS")
    logger.info("=" * 70)
    logger.info("")
    
    # Setup
    output_dir = Path('results/merfish')
    figures_dir = output_dir / 'figures'
    tables_dir = output_dir / 'tables'
    
    # Load data
    logger.info("STEP 1: Loading Data")
    logger.info("-" * 70)
    adata = load_example_merfish_data()
    logger.info("")
    
    # Analysis
    logger.info("STEP 2: Analysis")
    logger.info("-" * 70)
    adata = basic_analysis(adata, output_dir)
    logger.info("")
    
    # Visualizations
    logger.info("STEP 3: Visualizations")
    logger.info("-" * 70)
    create_visualizations(adata, str(figures_dir))
    logger.info("")
    
    # Statistics
    logger.info("STEP 4: Statistics")
    logger.info("-" * 70)
    stats = generate_statistics(adata, str(tables_dir))
    logger.info("")
    
    # Summary
    logger.info("=" * 70)
    logger.info("ANALYSIS COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Results saved to: {output_dir}")
    logger.info(f"  - Data: {output_dir}/processed_adata.h5ad")
    logger.info(f"  - Figures: {figures_dir}/")
    logger.info(f"  - Tables: {tables_dir}/")
    
    return adata


if __name__ == '__main__':
    adata = main()
