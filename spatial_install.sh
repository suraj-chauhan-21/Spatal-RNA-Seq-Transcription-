#!/bin/bash

################################################################################
# Spatial Transcriptomics Pipeline Installation Script
# Sets up conda environment and verifies dependencies
################################################################################

set -e

echo "=========================================="
echo "Spatial Transcriptomics Pipeline Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}✗ Conda not found. Please install Conda first.${NC}"
    echo "Download from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo -e "${GREEN}✓ Conda found${NC}"
echo ""

# Step 1: Create Conda Environment
echo -e "${BLUE}[STEP 1]${NC} Creating Conda environment 'spatial_env'..."
if conda env list | grep -q spatial_env; then
    echo -e "${YELLOW}Environment 'spatial_env' already exists. Skipping creation.${NC}"
else
    conda env create -f environment.yml
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Environment created successfully${NC}"
    else
        echo -e "${RED}✗ Environment creation failed${NC}"
        exit 1
    fi
fi

echo ""

# Step 2: Activate environment
echo -e "${BLUE}[STEP 2]${NC} Activating environment..."
source activate spatial_env

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Environment activated${NC}"
else
    echo -e "${RED}✗ Failed to activate environment${NC}"
    exit 1
fi

echo ""

# Step 3: Verify key packages
echo -e "${BLUE}[STEP 3]${NC} Verifying package installation..."

packages=("squidpy" "scanpy" "anndata" "pandas" "numpy")
missing_packages=()

for package in "${packages[@]}"; do
    python -c "import $package" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ${package}${NC} installed"
    else
        echo -e "${RED}✗ ${package}${NC} not installed"
        missing_packages+=("$package")
    fi
done

echo ""

# Step 4: Install missing packages if any
if [ ${#missing_packages[@]} -gt 0 ]; then
    echo -e "${YELLOW}Installing missing packages: ${missing_packages[@]}${NC}"
    pip install "${missing_packages[@]}"
fi

echo ""

# Step 5: Create directory structure
echo -e "${BLUE}[STEP 4]${NC} Creating project directory structure..."

directories=(
    "data"
    "data/raw"
    "data/processed"
    "results"
    "results/figures"
    "results/tables"
    "results/data"
    "results/report"
    "notebooks"
    "config"
    "logs"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    echo "  ✓ Created $dir"
done

echo ""

# Step 6: Test imports
echo -e "${BLUE}[STEP 5]${NC} Testing imports..."

python << 'EOF'
import sys
import importlib

packages = [
    'squidpy',
    'scanpy',
    'anndata',
    'pandas',
    'numpy',
    'matplotlib',
    'seaborn'
]

all_ok = True
for package in packages:
    try:
        mod = importlib.import_module(package)
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package}")
        all_ok = False

if all_ok:
    print("\n✓ All packages imported successfully!")
else:
    print("\n✗ Some packages failed to import")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All imports successful${NC}"
else
    echo -e "${RED}✗ Import test failed${NC}"
    exit 1
fi

echo ""

# Step 7: Final instructions
echo -e "${GREEN}=========================================="
echo "Setup completed successfully!"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Activate the environment:"
echo "   ${BLUE}conda activate spatial_env${NC}"
echo ""
echo "2. Edit configuration:"
echo "   ${BLUE}nano config/default_config.yaml${NC}"
echo ""
echo "3. Run example analysis:"
echo "   ${BLUE}python examples/merfish_example.py${NC}"
echo ""
echo "4. For Jupyter notebooks:"
echo "   ${BLUE}jupyter notebook${NC}"
echo ""
echo "5. View documentation:"
echo "   ${BLUE}cat README.md${NC}"
echo ""

# Create .env file for environment variables
cat > .env << 'ENVFILE'
# Spatial Transcriptomics Pipeline Environment Variables

# Paths
export PROJECT_ROOT=$(pwd)
export DATA_DIR="${PROJECT_ROOT}/data"
export RESULTS_DIR="${PROJECT_ROOT}/results"
export CONFIG_DIR="${PROJECT_ROOT}/config"
export NOTEBOOKS_DIR="${PROJECT_ROOT}/notebooks"

# Python path
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

# Parameters
export CONDA_ENV="spatial_env"
export PYTHON_VERSION="3.10"

echo "Environment variables loaded from $(pwd)/.env"
ENVFILE

echo -e "${BLUE}Environment variables file created (.env)${NC}"
echo ""

echo -e "${GREEN}Installation complete! 🎉${NC}"
