#!/bin/bash
# Verify Development Setup Script

set -e

echo "=========================================="
echo "Digital Human - Setup Verification"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅ $2${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}❌ $2${NC}"
        ((FAIL++))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}❌ $2${NC}"
        ((FAIL++))
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅ $2${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}❌ $2${NC}"
        ((FAIL++))
        return 1
    fi
}

# Check Python
echo "🐍 Checking Python..."
if check_command python "Python installed"; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    echo "   Version: $PYTHON_VERSION"
fi
echo ""

# Check virtual environment
echo "📦 Checking Virtual Environment..."
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
    ((PASS++))

    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
        echo "   Path: $VIRTUAL_ENV"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
        echo "   Run: source venv/bin/activate"
    fi
else
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "   Run: python -m venv venv"
    ((FAIL++))
fi
echo ""

# Check Python packages
echo "📚 Checking Python Packages..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    check_command pylint "Pylint installed"
    check_command mypy "MyPy installed"
    check_command bandit "Bandit installed"
    check_command pytest "Pytest installed"
    check_command pre-commit "Pre-commit installed"
else
    echo -e "${YELLOW}⚠️  Skipping package check (venv not activated)${NC}"
fi
echo ""

# Check configuration files
echo "⚙️  Checking Configuration Files..."
check_file ".pylintrc" "Pylint config exists"
check_file ".pre-commit-config.yaml" "Pre-commit config exists"
check_file ".bandit.yml" "Bandit config exists"
check_file ".editorconfig" "EditorConfig exists"
check_file "requirements.txt" "Requirements.txt exists"
check_file "requirements-dev.txt" "Dev requirements exists"
check_file "Makefile" "Makefile exists"
echo ""

# Check VS Code configuration
echo "💻 Checking VS Code Configuration..."
check_dir ".vscode" ".vscode directory exists"
check_file ".vscode/settings.json" "VS Code settings exist"
check_file ".vscode/extensions.json" "Extensions config exists"
check_file ".vscode/launch.json" "Launch config exists"
echo ""

# Check documentation
echo "📖 Checking Documentation..."
check_file "README.md" "README exists"
check_file "DEVELOPMENT.md" "Development guide exists"
check_file "QUICK_START_DEV.md" "Quick start guide exists"
check_file "CONTRIBUTING.md" "Contributing guide exists"
check_file "SETUP_SUMMARY.md" "Setup summary exists"
echo ""

# Check GitHub configuration
echo "🐙 Checking GitHub Configuration..."
check_dir ".github" ".github directory exists"
check_file ".github/workflows/pylint.yml" "Pylint workflow exists"
check_file ".github/PULL_REQUEST_TEMPLATE.md" "PR template exists"
echo ""

# Check Git hooks
echo "🪝 Checking Git Hooks..."
if [ -f ".git/hooks/pre-commit" ]; then
    echo -e "${GREEN}✅ Pre-commit hook installed${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️  Pre-commit hook not installed${NC}"
    echo "   Run: pre-commit install"
fi
echo ""

# Run quick tests if venv is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "🧪 Running Quick Tests..."

    echo -n "Testing pylint... "
    if pylint --version &> /dev/null; then
        echo -e "${GREEN}✅${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌${NC}"
        ((FAIL++))
    fi

    echo -n "Testing mypy... "
    if mypy --version &> /dev/null; then
        echo -e "${GREEN}✅${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌${NC}"
        ((FAIL++))
    fi

    echo -n "Testing bandit... "
    if bandit --version &> /dev/null; then
        echo -e "${GREEN}✅${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌${NC}"
        ((FAIL++))
    fi

    echo -n "Testing pytest... "
    if pytest --version &> /dev/null; then
        echo -e "${GREEN}✅${NC}"
        ((PASS++))
    else
        echo -e "${RED}❌${NC}"
        ((FAIL++))
    fi

    echo ""
fi

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo -e "Passed: ${GREEN}${PASS}${NC}"
echo -e "Failed: ${RED}${FAIL}${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Your development environment is ready! 🚀"
    echo ""
    echo "Next steps:"
    echo "  1. Activate venv: source venv/bin/activate"
    echo "  2. View commands: make help"
    echo "  3. Run app: make run-wav2lip"
    echo "  4. Read docs: QUICK_START_DEV.md"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some checks failed${NC}"
    echo ""
    echo "To fix issues:"
    echo "  1. Run setup script: ./scripts/setup_dev.sh"
    echo "  2. Install dependencies: make install-dev"
    echo "  3. Setup hooks: make setup-hooks"
    echo "  4. Read guide: DEVELOPMENT.md"
    exit 1
fi
