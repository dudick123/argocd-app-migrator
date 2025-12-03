# Contributing to ArgoCD ApplicationSet Migrator

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/argocd-app-migrator.git
   cd argocd-app-migrator
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clear, concise code
   - Follow existing code style
   - Add docstrings to functions
   - Update README if adding features

3. **Test your changes**:
   ```bash
   # Test the validate command
   python migrate.py validate ./examples/
   
   # Test dry run
   python migrate.py migrate ./examples/ \
     --config-repo https://example.com/repo.git \
     --dry-run
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request** on GitHub

## Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Add docstrings to all public functions
- Use meaningful variable names

## Adding New Features

When adding new features:

1. **Update the CLI**: Add new commands or options to `migrate.py`
2. **Update README**: Document the new feature with examples
3. **Add examples**: Include example files in `examples/` if relevant
4. **Test thoroughly**: Test with various ApplicationSet configurations

## Testing Guidelines

Before submitting a PR:

1. Test with real ApplicationSet files
2. Test both SCM and non-SCM ApplicationSets
3. Test error handling (invalid YAML, missing fields, etc.)
4. Test Azure DevOps integration if changes affect it
5. Verify dry-run mode works correctly

## Pull Request Guidelines

- Provide a clear description of changes
- Reference any related issues
- Include examples of the feature/fix in action
- Ensure all existing functionality still works
- Update documentation as needed

## Feature Ideas

Some ideas for future contributions:

- GitHub/GitLab integration for PR/MR creation
- Support for matrix generators
- Rollback functionality
- Interactive mode for selecting ApplicationSets
- Configuration file support (.migrator.yaml)
- Enhanced validation with detailed reports
- Support for additional template fields
- Batch processing with parallel execution
- Integration tests

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Review the README for documentation

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Focus on the problem, not the person

Thank you for contributing!
