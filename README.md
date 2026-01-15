# argocd-app-migrator

A CLI tool that migrates ArgoCD Application YAML manifests to JSON configuration files for ApplicationSets using Git Generators.

## Overview

This tool streamlines the migration from individual ArgoCD Application manifests to ApplicationSet configurations by:

1. Scanning directories for ArgoCD Application YAML files
2. Parsing and extracting relevant fields
3. Generating JSON configuration files compatible with ApplicationSet Git Generators
4. Validating output against JSON Schema

## Installation

### Prerequisites

- Python 3.12+
- UV package manager (recommended) or pip

### Install from source

```bash
# Clone the repository
git clone <repo-url>
cd argocd-app-migrator

# Create virtual environment
uv venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt

# Install in editable mode for development
uv pip install -e .
```

## Usage

### Basic Command

```bash
argocd-app-migrator --input-dir <directory>
# or using short flag
argocd-app-migrator -i <directory>
```

### Options

- `--input-dir, -i` (required): Directory containing ArgoCD Application YAML files
- `--output-dir, -o`: Specify output directory for JSON files (default: current directory)
- `--recursive, -r`: Scan directories recursively for YAML files
- `--dry-run`: Print output to terminal without writing files
- `--version, -v`: Show version and exit
- `--help`: Show help message

### Examples

```bash
# Basic migration
argocd-app-migrator --input-dir /path/to/argocd/apps

# Using short flags
argocd-app-migrator -i /path/to/argocd/apps

# Recursive scan with dry-run
argocd-app-migrator -i /path/to/argocd/apps --recursive --dry-run

# Custom output directory
argocd-app-migrator -i /path/to/argocd/apps -o /path/to/output

# Test with sample data
argocd-app-migrator -i io-artifact-examples/argocd-applications --dry-run
```

## Development

### Setup

```bash
# Install development dependencies
uv pip install -r requirements-dev.txt

# Install package in editable mode
uv pip install -e .
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint
flake8 src tests

# Type check
mypy src tests

# Run tests
pytest

# Run tests with coverage
pytest --cov-report=term-missing
```

### Project Structure

```
argocd-app-migrator/
├── src/argocd_app_migrator/  # Source code
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                # CLI implementation
│   └── version.py
├── tests/                    # Test suite
│   ├── conftest.py
│   └── test_cli.py
├── io-artifact-examples/     # Sample files
├── pyproject.toml           # Project configuration
├── requirements.txt         # Production dependencies
└── requirements-dev.txt     # Development dependencies
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_cli.py

# Run specific test class
pytest tests/test_cli.py::TestCLIBasics

# Run specific test method
pytest tests/test_cli.py::TestCLIBasics::test_version_flag

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src/argocd_app_migrator --cov-report=html
```

## Development Status

This project is currently in early development. The CLI shell is implemented, but the full migration pipeline (Scanner, Parser, Migrator, Validator) is coming soon.

## License

MIT
