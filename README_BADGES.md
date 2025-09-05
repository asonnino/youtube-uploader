# YouTube Uploader

[![CI](https://github.com/yourusername/youtube-uploader/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/youtube-uploader/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Simple Python script to upload YouTube videos from the command line

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/youtube-uploader.git
cd youtube-uploader

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=upload --cov-report=term-missing

# Run specific test file
pytest tests/test_upload.py -v
```

### Code Quality Checks

```bash
# Format code with Black
black .

# Check linting with flake8
flake8 .

# Type checking with mypy
mypy upload.py

# Spell checking
codespell

# Security checks
bandit -r .
safety check

# Run all pre-commit hooks
pre-commit run --all-files
```

### CI/CD

The project uses GitHub Actions for continuous integration. The CI pipeline:

- **Tests**: Runs on Python 3.9-3.13 across Ubuntu, macOS, and Windows
- **Code Quality**: Black formatting, flake8 linting, mypy type checking
- **Security**: Bandit and Safety vulnerability scanning
- **Spell Check**: Codespell for documentation and code comments

All checks run automatically on:
- Push to main/master branch
- Pull requests
- Manual workflow dispatch

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:
- Trailing whitespace removal
- End-of-file fixing
- YAML/JSON validation
- Large file detection
- Black code formatting
- isort import sorting
- Flake8 linting
- MyPy type checking
- Codespell
- Bandit security checks

To skip hooks temporarily: `git commit --no-verify`

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`pre-commit run --all-files`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request
