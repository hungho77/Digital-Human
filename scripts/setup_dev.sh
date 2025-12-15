#!/bin/bash
# Development Environment Setup Script for Digital Human

set -e  # Exit on error

echo "=========================================="
echo "Digital Human - Development Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Error: Python $REQUIRED_VERSION or higher is required."
    echo "   Current version: $PYTHON_VERSION"
    exit 1
fi
echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel --quiet
echo "✅ Package managers upgraded"
echo ""

# Install production dependencies
echo "Installing production dependencies..."
pip install -r requirements.txt --quiet
echo "✅ Production dependencies installed"
echo ""

# Install development dependencies
echo "Installing development dependencies..."
pip install -r requirements-dev.txt --quiet
echo "✅ Development dependencies installed"
echo ""

# Setup pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install
echo "✅ Pre-commit hooks installed"
echo ""

# Run initial checks
echo "Running initial code quality checks..."
echo ""

echo "1. Running pylint..."
if pylint $(git ls-files '*.py') --fail-under=7.0 --exit-zero --score=yes; then
    echo "✅ Pylint check passed"
else
    echo "⚠️  Pylint found some issues (this is normal for initial setup)"
fi
echo ""

echo "2. Running mypy..."
if mypy src/ --ignore-missing-imports --python-version=3.10 2>/dev/null; then
    echo "✅ Mypy check passed"
else
    echo "⚠️  Mypy found some type issues (this is normal for initial setup)"
fi
echo ""

echo "3. Running security checks..."
if bandit -r src/ -c .bandit.yml -q; then
    echo "✅ Security check passed"
else
    echo "⚠️  Bandit found some security issues (review recommended)"
fi
echo ""

echo "=========================================="
echo "✅ Development Environment Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the application:"
echo "     make run"
echo "     # or"
echo "     python app.py --model wav2lip --avatar_id avator_1"
echo ""
echo "  3. Open VS Code (recommended):"
echo "     code ."
echo ""
echo "  4. View available commands:"
echo "     make help"
echo ""
echo "Documentation:"
echo "  - DEVELOPMENT.md - Full development guide"
echo "  - README.md - Project overview"
echo "  - DOCKER.md - Docker deployment"
echo ""
echo "Happy coding! 🚀"

