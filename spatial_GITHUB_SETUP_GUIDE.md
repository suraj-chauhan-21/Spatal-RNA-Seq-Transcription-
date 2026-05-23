# 🚀 GitHub Repository Setup & Deployment Guide

## Complete Instructions to Upload to GitHub

### Phase 1: Prepare Your Local Repository

#### Step 1a: Create Local Directory Structure

```bash
# Create your project directory
mkdir spatial-transcriptomics
cd spatial-transcriptomics

# Initialize git
git init

# Create directory structure
mkdir -p src/spatial_pipeline tests config data/raw data/processed
mkdir -p notebooks examples docs/source .github/workflows
mkdir -p results/{figures,tables,data,report}

echo "# Spatial Transcriptomics Pipeline" > README.md
```

#### Step 1b: Copy All Files (Use Provided Files)

**From spatial_README.md:**
```bash
# Rename and place in root
cp spatial_README.md README.md
```

**Python Package Files:**
```bash
# Copy to src/spatial_pipeline/
cp spatial_main.py src/spatial_pipeline/__init__.py
cp spatial_visualization.py src/spatial_pipeline/visualization.py

# Create additional package files
# src/spatial_pipeline/io.py, preprocessing.py, clustering.py, analysis.py
# (Add skeleton versions or full implementations)

# Create __init__.py files
touch src/spatial_pipeline/__init__.py
touch tests/__init__.py
```

**Configuration Files:**
```bash
# Copy configs
cp spatial_environment.yml environment.yml
cp spatial_config.yaml config/default_config.yaml
cp spatial_config.yaml config/merfish_config.yaml

# Rename and copy gitignore
cp spatial_gitignore .gitignore
```

**Documentation:**
```bash
cp spatial_CONTRIBUTING.md CONTRIBUTING.md
cp spatial_CREATION_SUMMARY.md docs/CREATION_SUMMARY.md

# Create additional docs
touch docs/index.md docs/installation.md docs/faq.md
touch CODE_OF_CONDUCT.md
touch LICENSE (add MIT license text)
```

**Scripts and Setup:**
```bash
cp spatial_install.sh install.sh
cp spatial_setup.py setup.py
cp spatial_Makefile Makefile
```

**Examples:**
```bash
cp spatial_example_merfish.py examples/merfish_example.py
touch examples/visium_example.py examples/integration_example.py
touch examples/README.md
```

**Testing:**
```bash
cp spatial_tests.py tests/test_core.py
touch tests/conftest.py
```

**Docker:**
```bash
cp Dockerfile_spatial Dockerfile
touch .dockerignore
```

**GitHub Actions (Optional but Recommended):**
```bash
touch .github/workflows/tests.yml
touch .github/workflows/docs.yml
touch .github/workflows/publish.yml
```

#### Step 1c: Create Required Text Files

**LICENSE:**
```bash
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full MIT license text...]
EOF
```

**CODE_OF_CONDUCT.md:**
```bash
cat > CODE_OF_CONDUCT.md << 'EOF'
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone...

[Full code of conduct text...]
EOF
```

**docs/index.md:**
```bash
cat > docs/index.md << 'EOF'
# Spatial Transcriptomics Analysis Pipeline Documentation

Welcome to the comprehensive guide for the Spatial Transcriptomics Pipeline!

## Quick Links
- [Installation](installation.md)
- [Quick Start](../README.md#quick-start)
- [API Reference](api_reference.md)
- [Examples](../examples/)
- [Contributing](../CONTRIBUTING.md)

## Table of Contents
1. Installation and Setup
2. Data Loading
3. Quality Control
4. Clustering and Annotation
5. Advanced Analysis
6. Visualization
7. Troubleshooting
EOF
```

**docs/installation.md:**
```bash
cat > docs/installation.md << 'EOF'
# Installation Guide

## Prerequisites
- Linux/macOS/Windows (WSL)
- Conda (Miniconda or Anaconda)
- Python 3.10+
- 50GB free disk space

## Quick Install

\`\`\`bash
# Clone repository
git clone https://github.com/yourusername/spatial-transcriptomics.git
cd spatial-transcriptomics

# Run installation
bash install.sh

# Activate environment
conda activate spatial_env
\`\`\`

## Verification

\`\`\`bash
# Test imports
python -c "import squidpy, scanpy; print('✓ Installation successful')"
\`\`\`

[More detailed installation steps...]
EOF
```

---

### Phase 2: Commit to Local Repository

```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Complete spatial transcriptomics pipeline"

# Check status
git status
git log --oneline
```

---

### Phase 3: Create GitHub Repository

#### Step 3a: On GitHub Website

1. Go to https://github.com/new
2. Fill in details:
   - **Repository name:** `spatial-transcriptomics`
   - **Description:** "Comprehensive pipeline for spatial transcriptomics analysis using Squidpy and Scanpy"
   - **Visibility:** Public
   - **Initialize this repository with:** ❌ (Leave unchecked - you have files)
3. Click "Create repository"

#### Step 3b: Add Remote and Push

```bash
# Add remote (replace USERNAME with your GitHub username)
git remote add origin https://github.com/USERNAME/spatial-transcriptomics.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main

# Verify
git remote -v
```

---

### Phase 4: Configure GitHub Repository

#### Step 4a: Repository Settings

In GitHub Settings:

1. **General**
   - ✅ Enable Wikis (optional)
   - ✅ Enable Discussions
   - ✅ Enable Sponsorships (optional)

2. **Branch Protection**
   - Add rule for `main` branch
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass

3. **Actions**
   - ✅ Enable GitHub Actions

4. **Pages** (Optional - for documentation)
   - Source: Deploy from branch
   - Branch: main → /docs

#### Step 4b: Add Topics

Add these topics for discoverability:
- `spatial-transcriptomics`
- `squidpy`
- `scanpy`
- `bioinformatics`
- `single-cell`
- `merfish`
- `visium`
- `machine-learning`

---

### Phase 5: GitHub Actions (CI/CD)

#### Create .github/workflows/tests.yml

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
    
    - name: Lint with flake8
      run: flake8 src/ --max-line-length=100
    
    - name: Test with pytest
      run: pytest tests/ -v --cov=src
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

#### Create .github/workflows/docs.yml

```yaml
name: Documentation

on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install sphinx sphinx-rtd-theme
        pip install -e .
    
    - name: Build docs
      run: |
        cd docs
        make html
```

Push these files:
```bash
git add .github/workflows/
git commit -m "Add GitHub Actions for testing and docs"
git push origin main
```

---

### Phase 6: Create Release and Tags

```bash
# Create version tag
git tag -a v1.0.0 -m "Initial release"

# Push tags
git push origin v1.0.0

# Create release on GitHub (manually via web interface)
# Or via GitHub CLI:
# gh release create v1.0.0 --title "Version 1.0.0" --notes "Initial release"
```

---

### Phase 7: Documentation Setup

#### ReadTheDocs (Optional)

1. Go to https://readthedocs.org
2. Click "Sign up"
3. Connect GitHub account
4. Import project → select `spatial-transcriptomics`
5. Configure:
   - Python version: 3.10
   - Requirements file: requirements.txt
6. Build documentation

---

### Phase 8: Badge Setup

Add to README.md:

```markdown
[![Tests](https://github.com/USERNAME/spatial-transcriptomics/workflows/Tests/badge.svg)](https://github.com/USERNAME/spatial-transcriptomics/actions)
[![Documentation](https://readthedocs.org/projects/spatial-transcriptomics/badge/?version=latest)](https://spatial-transcriptomics.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![DOI](https://zenodo.org/badge/YOUR_ZENODO_ID.svg)](https://zenodo.org/badge/latestdoi/YOUR_ZENODO_ID)
```

---

## Final Checklist

- [x] All files committed to git
- [x] Repository created on GitHub
- [x] Main branch protected
- [x] GitHub Actions configured
- [x] README.md complete
- [x] CONTRIBUTING.md in place
- [x] LICENSE file added
- [x] CODE_OF_CONDUCT.md present
- [x] Example notebooks included
- [x] Tests passing
- [x] Documentation building
- [x] Release tags created
- [x] Topics added
- [x] Badges in README
- [x] .gitignore configured

---

## Publishing on PyPI (Optional)

### Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Create account
3. Create PyPI token
4. Store token securely

### Build and Upload

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Upload to TestPyPI first (optional)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*
```

Then users can install with:
```bash
pip install spatial-transcriptomics
```

---

## Sharing Your Repository

### Share with Collaborators

```bash
# Add collaborator via GitHub Settings → Collaborators
# Or use command line (requires push access):

# Invite via email
git remote add team https://github.com/team/spatial-transcriptomics.git
```

### Reference in Papers

Add to methods section:
```
Spatial transcriptomics analysis was performed using the spatial-transcriptomics 
pipeline (https://github.com/yourusername/spatial-transcriptomics, v1.0.0) 
built on Squidpy and Scanpy.
```

### Get DOI for Citation

1. Go to https://zenodo.org
2. Connect GitHub
3. Enable repository
4. Create release
5. Zenodo auto-creates DOI
6. Add DOI badge to README

---

## Troubleshooting

### Common Issues

**Issue: Files not appearing on GitHub**
```bash
# Check git status
git status

# Add all files
git add .

# Commit and push
git commit -m "Add files"
git push origin main
```

**Issue: Large files rejected**
```bash
# Git LFS for large files
git lfs install
git lfs track "*.h5ad"
git add .gitattributes
```

**Issue: GitHub Actions failing**
- Check workflow syntax
- Verify dependencies in requirements
- Check Python version compatibility
- Review error logs in Actions tab

---

## Maintenance

### Regular Maintenance

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update conda environment
conda env update -f environment.yml

# Run tests before releasing
pytest tests/ -v

# Create release
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

---

## Success Criteria

✅ Repository is public and discoverable  
✅ Installation works from GitHub  
✅ Tests pass automatically (CI/CD)  
✅ Documentation builds successfully  
✅ Examples run without errors  
✅ Users can install via pip  
✅ Contributing process is clear  
✅ Code is reproducible  

---

## Next Steps After Upload

1. **Share** - Post on social media, bioinformatics forums
2. **Gather Feedback** - Encourage issues and discussions
3. **Community** - Respond to questions and PRs
4. **Improve** - Incorporate feedback and updates
5. **Document** - Add more examples and tutorials
6. **Publish** - Consider publication about the tool

---

**Congratulations! Your repository is ready for the world! 🎉**

For questions or issues, refer to:
- GitHub Help: https://docs.github.com/en/get-started
- This guide's CONTRIBUTION.md
- Example analyses in /examples/

Good luck with your spatial transcriptomics research!
