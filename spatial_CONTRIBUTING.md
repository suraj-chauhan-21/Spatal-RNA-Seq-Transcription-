# Contributing to Spatial Transcriptomics Pipeline

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. All contributors are expected to uphold this code. Please report unacceptable behavior to [maintainer email].

## How to Contribute

### Ways to Contribute

1. **Code** - Fix bugs, add features, optimize performance
2. **Documentation** - Improve guides, add examples, fix typos
3. **Tests** - Write unit tests, integration tests, edge case tests
4. **Issues** - Report bugs, suggest features, provide feedback
5. **Examples** - Share notebooks, scripts, analysis workflows
6. **Data** - Contribute example datasets for testing

### Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/spatial-transcriptomics.git
   cd spatial-transcriptomics
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   bash install.sh
   conda activate spatial_env
   pip install -e ".[dev]"
   ```

4. **Make your changes** following the guidelines below

5. **Test your changes**
   ```bash
   pytest tests/
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "Add feature: description"
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request** on GitHub

## Development Setup

### Environment Setup

```bash
# Create development environment
conda env create -f environment.yml
conda activate spatial_env

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import spatial_pipeline; print('OK')"
```

### Project Structure

```
src/
├── spatial_pipeline/
│   ├── __init__.py
│   ├── io/              # Data input/output
│   ├── preprocessing/   # QC and normalization
│   ├── clustering/      # Clustering methods
│   ├── analysis/        # Advanced analysis
│   ├── visualization/   # Plotting functions
│   └── core/            # Core classes
tests/
├── test_io.py
├── test_preprocessing.py
├── test_clustering.py
└── test_visualization.py
notebooks/
├── Example notebooks
examples/
├── Example scripts
```

## Coding Standards

### Python Style Guide

Follow PEP 8 with these guidelines:

```python
# Imports (organized)
import os
import logging
from pathlib import Path
from typing import Optional, Dict

import numpy as np
import pandas as pd
import anndata as ad

# Functions should have docstrings
def process_spatial_data(
    adata: ad.AnnData,
    n_neighbors: int = 6,
    use_spatial: bool = True
) -> ad.AnnData:
    """
    Process spatial transcriptomics data.
    
    Parameters
    ----------
    adata : anndata.AnnData
        Input data
    n_neighbors : int
        Number of neighbors for spatial graph
    use_spatial : bool
        Whether to use spatial coordinates
        
    Returns
    -------
    anndata.AnnData
        Processed data
        
    Examples
    --------
    >>> adata = process_spatial_data(adata)
    """
    # Implementation
    pass

# Classes with clear documentation
class SpatialAnalyzer:
    """Analyze spatial transcriptomics data."""
    
    def __init__(self, adata: ad.AnnData):
        """Initialize analyzer."""
        self.adata = adata
```

### Code Quality

```bash
# Format code with black
black src/

# Check style with flake8
flake8 src/

# Type checking with mypy
mypy src/

# All-in-one check
make lint
```

## Testing

### Write Tests

```python
# tests/test_preprocessing.py
import pytest
import numpy as np
import anndata as ad

@pytest.fixture
def sample_adata():
    """Create test data."""
    return ad.AnnData(X=np.random.rand(100, 50))

def test_normalization(sample_adata):
    """Test normalization function."""
    from spatial_pipeline.preprocessing import normalize
    
    normalized = normalize(sample_adata)
    assert normalized.X.sum(axis=1).mean() == pytest.approx(1.0, rel=0.1)

def test_clustering(sample_adata):
    """Test clustering function."""
    from spatial_pipeline.clustering import leiden_clustering
    
    result = leiden_clustering(sample_adata)
    assert 'leiden' in result.obs
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_preprocessing.py::test_normalization -v

# Run with markers
pytest -m integration
```

## Submitting Changes

### Pull Request Process

1. **Update documentation** if changing functionality
2. **Add tests** for new features
3. **Update CHANGELOG.md** with your changes
4. **Ensure all tests pass** locally
5. **Provide clear PR description**

### PR Template

```markdown
## Description
Brief description of changes

## Related Issue
Fixes #[issue number]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] No breaking changes
```

## Reporting Bugs

### Bug Report Template

```markdown
## Description
Clear description of the bug

## Environment
- OS: [Linux/macOS/Windows]
- Python version: [e.g., 3.10]
- squidpy version: [e.g., 1.2.0]

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Error Messages
```
[Paste error traceback]
```

## Additional Context
Any other relevant information
```

## Suggesting Enhancements

### Feature Request Template

```markdown
## Description
Clear description of the feature

## Motivation
Why would this be useful?

## Implementation Ideas
How might this be implemented?

## Examples
Usage examples or mockups
```

## Guidelines

### General

- Be respectful and constructive
- Follow existing code patterns
- Write clear commit messages
- Keep PRs focused on single features
- Update docs with code changes

### Documentation

- Add docstrings to all functions/classes
- Use reStructuredText format
- Include examples in docstrings
- Update README if needed
- Update relevant markdown files

### Testing

- Aim for >80% code coverage
- Write tests before code (TDD)
- Test edge cases
- Include integration tests
- Test error handling

### Performance

- Consider memory usage
- Optimize for large datasets
- Profile before optimizing
- Document performance characteristics

## Resources

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Documentation](docs/index.md)
- [API Reference](docs/api_reference.md)
- [Squidpy Docs](https://squidpy.readthedocs.io/)
- [Scanpy Docs](https://scanpy.readthedocs.io/)

## Questions?

- Check existing issues and discussions
- Read the documentation
- Open a new discussion
- Contact maintainers

---

Thank you for contributing! Your help makes this project better. 🙏
