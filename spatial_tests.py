"""
Unit tests for Spatial Transcriptomics Pipeline
"""

import pytest
import numpy as np
import pandas as pd
import anndata as ad
import squidpy as sq
from pathlib import Path
import tempfile
import yaml


@pytest.fixture
def sample_adata():
    """Create a sample AnnData object with spatial coordinates"""
    n_obs = 100
    n_vars = 50
    
    X = np.random.poisson(5, (n_obs, n_vars)).astype(np.float32)
    obs = pd.DataFrame(
        {'sample': np.repeat(['A', 'B'], n_obs // 2)},
        index=pd.Index([f'cell_{i}' for i in range(n_obs)], name='cell_id')
    )
    var = pd.DataFrame(
        {'gene_names': [f'gene_{i}' for i in range(n_vars)]},
        index=pd.Index([f'gene_{i}' for i in range(n_vars)], name='gene_id')
    )
    spatial = np.random.rand(n_obs, 2) * 100
    
    adata = ad.AnnData(X=X, obs=obs, var=var)
    adata.obsm['spatial'] = spatial
    
    return adata


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for outputs"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def config_dict():
    """Create sample configuration dictionary"""
    return {
        'data': {
            'platform': 'merfish',
            'data_path': 'data/sample.h5ad'
        },
        'qc': {
            'min_counts': 100,
            'min_genes': 50,
            'max_mt_pct': 20
        },
        'clustering': {
            'resolution': 0.5,
            'use_spatial': True
        }
    }


class TestSpatialData:
    """Test spatial data structure and properties"""
    
    def test_adata_creation(self, sample_adata):
        """Test AnnData object creation"""
        assert sample_adata.n_obs == 100
        assert sample_adata.n_vars == 50
        assert 'spatial' in sample_adata.obsm
        assert sample_adata.obsm['spatial'].shape == (100, 2)
    
    def test_spatial_coordinates_range(self, sample_adata):
        """Test spatial coordinates are in valid range"""
        coords = sample_adata.obsm['spatial']
        assert np.all(coords >= 0)
        assert np.all(coords <= 100)
    
    def test_gene_expression_shape(self, sample_adata):
        """Test gene expression matrix shape"""
        assert sample_adata.X.shape == (100, 50)


class TestPreprocessing:
    """Test preprocessing functions"""
    
    def test_qc_metrics_calculation(self, sample_adata):
        """Test QC metrics calculation"""
        import scanpy as sc
        
        sc.pp.calculate_qc_metrics(sample_adata, inplace=True)
        
        assert 'n_counts' in sample_adata.obs
        assert 'n_genes' in sample_adata.obs
        assert all(sample_adata.obs['n_counts'] > 0)
    
    def test_normalization(self, sample_adata):
        """Test normalization"""
        import scanpy as sc
        
        X_before = sample_adata.X.copy()
        
        sc.pp.normalize_total(sample_adata, inplace=True)
        sc.pp.log1p(sample_adata)
        
        X_after = sample_adata.X
        
        # Check that data changed
        assert not np.allclose(X_before, X_after)
    
    def test_hvg_selection(self, sample_adata):
        """Test highly variable gene selection"""
        import scanpy as sc
        
        sc.pp.normalize_total(sample_adata, inplace=True)
        sc.pp.log1p(sample_adata)
        sc.pp.highly_variable_genes(sample_adata, n_top_genes=10, inplace=True)
        
        assert 'highly_variable' in sample_adata.var
        assert sample_adata.var['highly_variable'].sum() == 10


class TestClustering:
    """Test clustering functions"""
    
    def test_spatial_neighbors(self, sample_adata):
        """Test spatial neighbors computation"""
        import squidpy as sq
        
        sq.gr.spatial_neighbors(sample_adata, n_neighbors=5)
        
        assert 'spatial_neighbors' in sample_adata.obsp
        assert sample_adata.obsp['spatial_neighbors'].shape == (100, 100)
    
    def test_leiden_clustering(self, sample_adata):
        """Test Leiden clustering"""
        import scanpy as sc
        
        # Prepare data
        sc.pp.neighbors(sample_adata, use_rep='X')
        sc.tl.leiden(sample_adata, resolution=0.5)
        
        assert 'leiden' in sample_adata.obs
        assert sample_adata.obs['leiden'].dtype.name == 'category'


class TestConfiguration:
    """Test configuration handling"""
    
    def test_config_loading(self, config_dict, temp_output_dir):
        """Test configuration dictionary"""
        assert 'data' in config_dict
        assert 'qc' in config_dict
        assert config_dict['data']['platform'] == 'merfish'
    
    def test_config_yaml_save(self, config_dict, temp_output_dir):
        """Test saving config to YAML"""
        config_path = temp_output_dir / 'config.yaml'
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f)
        
        with open(config_path, 'r') as f:
            loaded = yaml.safe_load(f)
        
        assert loaded == config_dict


class TestVisualization:
    """Test visualization functions"""
    
    def test_visualizer_initialization(self, sample_adata, temp_output_dir):
        """Test visualizer initialization"""
        from spatial_visualization import SpatialVisualizer
        
        viz = SpatialVisualizer(
            sample_adata,
            output_dir=str(temp_output_dir),
            figsize=(8, 8),
            dpi=100,
            format='png'
        )
        
        assert viz.adata is sample_adata
        assert viz.output_dir.exists()
    
    def test_spatial_scatter_plotting(self, sample_adata, temp_output_dir):
        """Test spatial scatter plot creation"""
        from spatial_visualization import SpatialVisualizer
        
        sample_adata.obs['cell_type'] = np.repeat(['A', 'B'], 50)
        
        viz = SpatialVisualizer(
            sample_adata,
            output_dir=str(temp_output_dir),
            figsize=(8, 8),
            format='png'
        )
        
        # Should not raise error
        viz.spatial_scatter(
            color='cell_type',
            save_name='test_scatter',
            show=False
        )


class TestPipeline:
    """Test main pipeline class"""
    
    def test_pipeline_initialization(self, config_dict, temp_output_dir):
        """Test pipeline initialization"""
        config_path = temp_output_dir / 'config.yaml'
        
        with open(config_path, 'w') as f:
            yaml.dump(config_dict, f)
        
        from spatial_main import SpatialAnalysisPipeline
        
        pipeline = SpatialAnalysisPipeline(
            str(config_path),
            output_dir=str(temp_output_dir)
        )
        
        assert pipeline.config == config_dict
        assert pipeline.output_dir.exists()


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_basic_workflow(self, sample_adata, temp_output_dir):
        """Test basic analysis workflow"""
        import scanpy as sc
        import squidpy as sq
        
        # QC
        sc.pp.calculate_qc_metrics(sample_adata, inplace=True)
        
        # Normalize
        sc.pp.normalize_total(sample_adata, inplace=True)
        sc.pp.log1p(sample_adata)
        
        # HVG
        sc.pp.highly_variable_genes(sample_adata, n_top_genes=10, inplace=True)
        
        # Clustering
        sc.pp.neighbors(sample_adata, use_rep='X')
        sc.tl.leiden(sample_adata, resolution=0.5)
        
        # Spatial analysis
        sq.gr.spatial_neighbors(sample_adata, n_neighbors=5)
        
        assert 'leiden' in sample_adata.obs
        assert 'spatial_neighbors' in sample_adata.obsp


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
