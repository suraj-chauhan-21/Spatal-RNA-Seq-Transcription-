"""
Visualization module for spatial transcriptomics data
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scanpy as sc
import squidpy as sq
import anndata as ad

logger = logging.getLogger(__name__)


class SpatialVisualizer:
    """
    Comprehensive visualization class for spatial transcriptomics data
    
    Parameters
    ----------
    adata : anndata.AnnData
        Annotated data object with spatial coordinates
    output_dir : str
        Output directory for saving figures
    figsize : tuple
        Default figure size (width, height)
    dpi : int
        Resolution for saved figures
    format : str
        Output format ('pdf', 'png', 'svg')
    """
    
    def __init__(
        self,
        adata: ad.AnnData,
        output_dir: str = 'figures/',
        figsize: Tuple[int, int] = (10, 10),
        dpi: int = 300,
        format: str = 'pdf'
    ):
        """Initialize visualizer"""
        self.adata = adata
        self.output_dir = Path(output_dir)
        self.figsize = figsize
        self.dpi = dpi
        self.format = format
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.facecolor'] = 'white'
        
        logger.info(f"Visualizer initialized with output: {self.output_dir}")
    
    def spatial_scatter(
        self,
        color: Optional[str] = None,
        size: int = 30,
        alpha: float = 0.8,
        cmap: str = 'viridis',
        title: Optional[str] = None,
        save_name: Optional[str] = None,
        show: bool = False
    ) -> None:
        """
        Create spatial scatter plot
        
        Parameters
        ----------
        color : str, optional
            Column in adata.obs for coloring
        size : int
            Marker size
        alpha : float
            Transparency
        cmap : str
            Colormap name
        title : str, optional
            Plot title
        save_name : str, optional
            Name for saved file
        show : bool
            If True, display plot
        """
        try:
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
            
            # Get spatial coordinates
            coords = self.adata.obsm['spatial']
            
            # Create scatter plot
            if color and color in self.adata.obs.columns:
                # Categorical or continuous coloring
                if pd.api.types.is_categorical_dtype(self.adata.obs[color]):
                    # Categorical
                    categories = self.adata.obs[color].cat.categories
                    colors = plt.cm.get_cmap('tab20')(np.linspace(0, 1, len(categories)))
                    
                    for i, cat in enumerate(categories):
                        mask = self.adata.obs[color] == cat
                        ax.scatter(
                            coords[mask, 0],
                            coords[mask, 1],
                            s=size,
                            alpha=alpha,
                            label=cat,
                            color=colors[i]
                        )
                    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                else:
                    # Continuous
                    scatter = ax.scatter(
                        coords[:, 0],
                        coords[:, 1],
                        c=self.adata.obs[color],
                        s=size,
                        alpha=alpha,
                        cmap=cmap
                    )
                    plt.colorbar(scatter, ax=ax)
            else:
                # No coloring
                ax.scatter(coords[:, 0], coords[:, 1], s=size, alpha=alpha)
            
            ax.set_xlabel('X (µm)')
            ax.set_ylabel('Y (µm)')
            ax.set_aspect('equal')
            
            if title:
                ax.set_title(title, fontsize=14, fontweight='bold')
            
            if save_name:
                save_path = self.output_dir / f"{save_name}.{self.format}"
                plt.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
                logger.info(f"Figure saved: {save_path}")
            
            if show:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Spatial scatter plot failed: {e}")
            raise
    
    def gene_expression_map(
        self,
        gene: str,
        size: int = 30,
        alpha: float = 0.8,
        cmap: str = 'YlOrRd',
        vmin: Optional[float] = None,
        vmax: Optional[float] = None,
        save_name: Optional[str] = None,
        show: bool = False
    ) -> None:
        """
        Create gene expression spatial map
        
        Parameters
        ----------
        gene : str
            Gene name to plot
        size : int
            Marker size
        alpha : float
            Transparency
        cmap : str
            Colormap name
        vmin : float, optional
            Minimum value for colorscale
        vmax : float, optional
            Maximum value for colorscale
        save_name : str, optional
            Name for saved file
        show : bool
            If True, display plot
        """
        try:
            if gene not in self.adata.var_names:
                logger.warning(f"Gene {gene} not found in data")
                return
            
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
            
            # Get gene expression
            gene_expr = self.adata[:, gene].X.toarray().flatten()
            coords = self.adata.obsm['spatial']
            
            # Set value range
            if vmin is None:
                vmin = np.min(gene_expr)
            if vmax is None:
                vmax = np.percentile(gene_expr, 99)
            
            scatter = ax.scatter(
                coords[:, 0],
                coords[:, 1],
                c=gene_expr,
                s=size,
                alpha=alpha,
                cmap=cmap,
                vmin=vmin,
                vmax=vmax
            )
            
            ax.set_xlabel('X (µm)')
            ax.set_ylabel('Y (µm)')
            ax.set_aspect('equal')
            ax.set_title(f'{gene} Expression', fontsize=14, fontweight='bold')
            
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('Log-normalized Expression', rotation=270, labelpad=20)
            
            if save_name:
                save_path = self.output_dir / f"{save_name}.{self.format}"
                plt.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
                logger.info(f"Figure saved: {save_path}")
            
            if show:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Gene expression map failed: {e}")
            raise
    
    def cluster_map(
        self,
        cluster_key: str = 'leiden',
        size: int = 30,
        alpha: float = 0.8,
        show_legend: bool = True,
        save_name: Optional[str] = None,
        show: bool = False
    ) -> None:
        """
        Create spatial cluster map
        
        Parameters
        ----------
        cluster_key : str
            Key in adata.obs for cluster labels
        size : int
            Marker size
        alpha : float
            Transparency
        show_legend : bool
            If True, show legend
        save_name : str, optional
            Name for saved file
        show : bool
            If True, display plot
        """
        try:
            if cluster_key not in self.adata.obs.columns:
                logger.warning(f"Cluster key {cluster_key} not found")
                return
            
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
            
            coords = self.adata.obsm['spatial']
            clusters = self.adata.obs[cluster_key]
            
            # Use color palette
            n_clusters = len(clusters.cat.categories) if hasattr(clusters, 'cat') else len(set(clusters))
            colors = plt.cm.get_cmap('tab20')(np.linspace(0, 1, min(n_clusters, 20)))
            
            for i, cluster_id in enumerate(clusters.unique()):
                mask = clusters == cluster_id
                ax.scatter(
                    coords[mask, 0],
                    coords[mask, 1],
                    s=size,
                    alpha=alpha,
                    label=str(cluster_id),
                    color=colors[i % len(colors)]
                )
            
            ax.set_xlabel('X (µm)')
            ax.set_ylabel('Y (µm)')
            ax.set_aspect('equal')
            ax.set_title(f'Spatial Clusters ({cluster_key})', fontsize=14, fontweight='bold')
            
            if show_legend:
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', ncol=2)
            
            if save_name:
                save_path = self.output_dir / f"{save_name}.{self.format}"
                plt.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
                logger.info(f"Figure saved: {save_path}")
            
            if show:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Cluster map creation failed: {e}")
            raise
    
    def heatmap_genes(
        self,
        genes: List[str],
        cluster_key: str = 'leiden',
        save_name: Optional[str] = None,
        show: bool = False
    ) -> None:
        """
        Create heatmap of gene expression by cluster
        
        Parameters
        ----------
        genes : list
            List of gene names
        cluster_key : str
            Key in adata.obs for cluster labels
        save_name : str, optional
            Name for saved file
        show : bool
            If True, display plot
        """
        try:
            # Check genes
            genes = [g for g in genes if g in self.adata.var_names]
            if not genes:
                logger.warning("No valid genes found")
                return
            
            # Get mean expression per cluster
            expr_df = pd.DataFrame(
                self.adata[:, genes].X.toarray(),
                columns=genes,
                index=self.adata.obs[cluster_key]
            )
            expr_means = expr_df.groupby(level=0).mean()
            
            fig, ax = plt.subplots(figsize=(max(len(genes), 10), max(len(expr_means), 5)))
            
            sns.heatmap(
                expr_means.T,
                cmap='RdYlBu_r',
                cbar_kws={'label': 'Mean Expression'},
                ax=ax,
                annot=False,
                fmt='.2f'
            )
            
            ax.set_title('Gene Expression by Cluster', fontsize=14, fontweight='bold')
            ax.set_xlabel(f'Clusters ({cluster_key})')
            ax.set_ylabel('Genes')
            
            if save_name:
                save_path = self.output_dir / f"{save_name}.{self.format}"
                plt.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
                logger.info(f"Figure saved: {save_path}")
            
            if show:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Heatmap creation failed: {e}")
            raise
    
    def multi_gene_spatial(
        self,
        genes: List[str],
        n_cols: int = 3,
        size: int = 20,
        save_name: Optional[str] = None,
        show: bool = False
    ) -> None:
        """
        Create multi-panel spatial gene expression plot
        
        Parameters
        ----------
        genes : list
            List of gene names to plot
        n_cols : int
            Number of columns in subplot grid
        size : int
            Marker size
        save_name : str, optional
            Name for saved file
        show : bool
            If True, display plot
        """
        try:
            genes = [g for g in genes if g in self.adata.var_names]
            n_genes = len(genes)
            n_rows = int(np.ceil(n_genes / n_cols))
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 4*n_rows))
            axes = axes.flatten()
            
            coords = self.adata.obsm['spatial']
            
            for idx, gene in enumerate(genes):
                ax = axes[idx]
                gene_expr = self.adata[:, gene].X.toarray().flatten()
                
                scatter = ax.scatter(
                    coords[:, 0],
                    coords[:, 1],
                    c=gene_expr,
                    s=size,
                    cmap='YlOrRd',
                    alpha=0.8
                )
                
                ax.set_title(gene, fontsize=12, fontweight='bold')
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_aspect('equal')
                plt.colorbar(scatter, ax=ax)
            
            # Hide unused subplots
            for idx in range(n_genes, len(axes)):
                axes[idx].set_visible(False)
            
            plt.tight_layout()
            
            if save_name:
                save_path = self.output_dir / f"{save_name}.{self.format}"
                plt.savefig(save_path, bbox_inches='tight', dpi=self.dpi)
                logger.info(f"Figure saved: {save_path}")
            
            if show:
                plt.show()
            
            plt.close()
            
        except Exception as e:
            logger.error(f"Multi-gene plot failed: {e}")
            raise


if __name__ == '__main__':
    # Example usage
    pass
