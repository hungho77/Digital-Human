# Contributing to Digital Human

Thank you for your interest in contributing to Digital Human! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, model used)
- **Error messages** and stack traces
- **Screenshots** if applicable

### Suggesting Features

Feature requests are welcome! Please provide:

- **Clear description** of the feature
- **Use case** explaining why it's needed
- **Proposed implementation** (if you have ideas)
- **Alternative solutions** you've considered

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following our standards
4. **Run quality checks** (`make check`)
5. **Commit your changes** (see commit guidelines below)
6. **Push to your fork** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

## 🛠️ Development Setup

### Quick Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Digital-Human.git
cd Digital-Human

# Run automated setup
./scripts/setup_dev.sh
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install
```

For detailed setup instructions, see [QUICK_START_DEV.md](QUICK_START_DEV.md).

## 📝 Code Standards

### Required Standards

All contributions must follow these standards:

1. **Google-style Docstrings**
   ```python
   def example_function(param: str) -> bool:
       """Brief description.

       Longer description if needed.

       Args:
           param: Description of parameter.

       Returns:
           Description of return value.

       Raises:
           ValueError: When something goes wrong.
       """
       return True
   ```

2. **Type Hints**
   ```python
   from typing import Dict, List, Optional

   def process(data: List[str], config: Optional[Dict] = None) -> bool:
       """Process data with optional config."""
       pass
   ```

3. **Specific Exception Handling**
   ```python
   # Good ✅
   try:
       result = process_file(path)
   except FileNotFoundError as e:
       logger.error(f"File not found: {e}")
       raise

   # Bad ❌
   try:
       result = process_file(path)
   except Exception as e:
       logger.error(f"Error: {e}")
   ```

4. **Code Quality**
   - Pylint score ≥ 7.0
   - MyPy type checking passes
   - Bandit security checks pass
   - All tests pass

### Code Style

- **Line Length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Line Endings**: Unix (LF)
- **Trailing Whitespace**: None
- **Final Newline**: Required

## ✅ Pre-Commit Checklist

Before committing, ensure:

```bash
# Run all quality checks
make check

# Run tests
make test

# Or run full CI pipeline
make ci
```

Your checklist:
- [ ] Code follows Google-style docstrings
- [ ] All functions have type hints
- [ ] Pylint score ≥ 7.0
- [ ] MyPy passes
- [ ] Bandit passes
- [ ] All tests pass
- [ ] Pre-commit hooks pass
- [ ] Documentation updated
- [ ] No debug code or commented code

## 📋 Commit Guidelines

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(tts): add EdgeTTS voice selection

- Implemented voice selection UI
- Added voice preview functionality
- Updated TTS configuration options

Closes #123
```

```
fix(webrtc): resolve connection timeout issue

Fixed timeout when connecting to STUN server by increasing
the timeout threshold and adding retry logic.

Fixes #456
```

### Rules

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- First line should be ≤ 72 characters
- Reference issues and PRs when relevant
- Explain *what* and *why*, not *how*

## 🧪 Testing Guidelines

### Writing Tests

Place tests in `tests/` directory:

```python
import pytest
from src.services.real import ensure_model_loaded

def test_ensure_model_loaded():
    """Test model loading functionality."""
    # Test implementation
    pass

@pytest.mark.asyncio
async def test_async_function():
    """Test async functionality."""
    # Async test
    pass
```

### Running Tests

```bash
# All tests
make test

# With coverage
make test-cov

# Specific file
pytest tests/test_services.py

# Verbose
pytest -v
```

### Coverage Requirements

- New features should include tests
- Aim for 80%+ coverage
- Critical paths must be tested

## 🔍 Code Review Process

### For Contributors

When you submit a PR:

1. Fill out the PR template completely
2. Ensure all checks pass
3. Respond to reviewer feedback
4. Keep commits clean and organized

### For Reviewers

When reviewing PRs:

1. Check code quality and standards
2. Verify tests are adequate
3. Test the changes locally
4. Provide constructive feedback
5. Approve when ready

## 🏗️ Project Architecture

### Directory Structure

```
src/
├── api/           # Web server and API endpoints
├── core/          # Base classes (BaseReal, BaseASR)
├── modules/       # AI model implementations
│   ├── musetalk/  # MuseTalk model
│   ├── wav2lip/   # Wav2Lip model
│   └── ultralight/# Ultralight model
├── services/      # External services (TTS, LLM, WebRTC)
└── utils/         # Utilities
```

### Adding New Features

#### New TTS Service

1. Implement in `src/services/tts.py`
2. Follow existing TTS service patterns
3. Add configuration options
4. Update documentation

#### New AI Model

1. Create module in `src/modules/`
2. Inherit from `BaseReal`
3. Implement required methods
4. Register in `src/services/unified_real.py`
5. Add tests

## 📚 Documentation

### Required Documentation

- **Code Comments**: For complex logic
- **Docstrings**: For all public functions/classes
- **README Updates**: For user-facing changes
- **DEVELOPMENT.md**: For developer-facing changes
- **Examples**: For new features

### Documentation Style

- Use Markdown for all documentation
- Include code examples
- Keep it up-to-date
- Add screenshots when helpful

## 🐛 Debugging Tips

### Common Issues

1. **Import Errors**
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Pre-commit Failures**
   ```bash
   pre-commit run --all-files
   ```

3. **Test Failures**
   ```bash
   pytest -v -s  # Verbose with output
   ```

### Debug Mode

```bash
# Run with debug logging
python app.py --debug

# Use VS Code debugger (F5)
# Or use ipdb
import ipdb; ipdb.set_trace()
```

## 🎯 Areas for Contribution

We especially welcome contributions in:

- **New TTS Services**: Additional voice synthesis integrations
- **Model Improvements**: Enhancements to existing AI models
- **Documentation**: Tutorials, guides, examples
- **Testing**: Improving test coverage
- **Performance**: Optimization and profiling
- **Bug Fixes**: Resolving open issues
- **UI/UX**: Web interface improvements

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open an Issue
- **Security**: See SECURITY.md
- **Chat**: Join our community (if available)

## 📄 License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## 🙏 Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- Project documentation

Thank you for contributing to Digital Human! 🚀

