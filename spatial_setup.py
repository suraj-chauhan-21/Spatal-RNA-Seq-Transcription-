"""
Setup configuration for Spatial Transcriptomics Pipeline
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="spatial-transcriptomics",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@institution.org",
    description="Comprehensive pipeline for spatial transcriptomics analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/spatial-transcriptomics",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/spatial-transcriptomics/issues",
        "Documentation": "https://spatial-transcriptomics.readthedocs.io",
        "Source Code": "https://github.com/yourusername/spatial-transcriptomics",
    },
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.21",
        "pandas>=1.3",
        "scipy>=1.7",
        "scikit-learn>=1.0",
        "scikit-image>=0.18",
        "matplotlib>=3.5",
        "seaborn>=0.11",
        "scanpy>=1.9",
        "anndata>=0.9",
        "squidpy>=1.2",
        "spatialdata>=0.0.14",
        "plotly>=5.0",
        "networkx>=2.6",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
            "sphinx>=4.5",
            "sphinx-rtd-theme>=1.0",
        ],
        "gpu": [
            "torch>=1.12.0",
            "rapids-xgboost>=2.1",
        ],
        "analysis": [
            "cellchat>=1.4",
            "tangram-sc>=1.0",
            "decoupler>=1.3",
            "pertpy>=0.8",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "spatial transcriptomics",
        "single-cell genomics",
        "MERFISH",
        "Visium",
        "bioinformatics",
        "RNA-seq",
    ],
    zip_safe=False,
    include_package_data=True,
)
