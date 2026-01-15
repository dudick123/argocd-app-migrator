# Overview

This is a CLI tool that scans an input directory for ArgoCD Application YAML manifests, extracts relevant information, and generates JSON configuration files for new ApplicationSets using Git Generators. The current TODO list at the bottom of this document outlines the steps needed to complete the implementation.

## NEVER EVER DO THE FOLLOWING

These rules are ABSOLUTE:

### NEVER Publish Sensitive Data

- NEVER publish passwords, API keys, tokens to git/npm/docker
- Before ANY commit: verify no secrets included

### NEVER Commit .env Files

- NEVER commit `.env` to git
- ALWAYS verify `.env` is in `.gitignore`

### NEVER Hardcode Credentials

- ALWAYS use environment variables

## Best Practices

### Required Structure

project/
├── src/
├── tests/
├── docs/
├── .claude/commands/
└── scripts/

### Required Files (Create Immediately If Missing)

- `.env` — Environment variables (NEVER commit)
- `.env.example` — Template with placeholder values
- `.gitignore` — Must include: .env, .env.*, node_modules/, dist/, .claude/
- `.dockerignore` — Must include: .env, .git/, node_modules/
- `README.md` — Project overview (reference env vars, don't hardcode)

### Python Project Best Practices To Follow

- Create `pyproject.toml` (not setup.py)
- Use `src/` layout
- Include `requirements.txt` AND `requirements-dev.txt`
- Add `.python-version` file
- Use `uv` for package management
- Use `typer` for CLI interfaces
- Use `rich` for enhanced terminal output and logging
- Include type hints and use `mypy` for type checking
- Write unit tests with `pytest` and achieve high test coverage
- Use `black` for code formatting
- Use `isort` for import sorting
- Use `flake8` for linting
- Include a `tests/` directory with test cases
- Set up CI/CD pipelines for automated testing and deployment

### Docker Best Practices To Follow

- Use official, hardened base images
- Multi-stage builds ALWAYS
- Never run as root (use non-root user)
- Include health checks
- `.dockerignore` must mirror `.gitignore` + include `.git/`

## Quality Requirements

### File Size Limits

- No file > 300 lines (split if larger)
- No function > 50 lines

### Required Before Commit

- All tests pass
- Python runs with no errors
- Linter passes with no warnings
- No secrets in staged files

### CI/CD Requirements

The project must include:

- `.github/workflows/ci.yml` for GitHub Actions
- Pre-commit hooks via pre-commit for Python)

## Example Files

Example ApplicationSet YAML files can be found in the `io-artifact-examples` directories. The following directories contain sample manifests for input validation and testing:

- `io-artifact-examples/applicationset-generator-config` - Contains an example JSON file that will be the result of a migration.
- `io-artifact-examples/argocd-application-sets` - Contains various ApplicationSet YAML files that implement a Git Generator.
- `io-artifact-examples/argocd-applications` - Contains ArgoCD Application YAML files that that will be converted to a JSON configuration for new ApplicationSets.

## Tech Stack

- Python 3.12+
- UV for package management
- Typer for CLI interface
- PyYAML for YAML parsing
- Rich for enhanced terminal output and logging
- jsonschema for JSON Schema validation

## Basic Data Flow

1. Read a directory path from command-line input.
2. Scan the directory for ArgoCD Application YAML files. If specified, scan recursively.
3. Parse each YAML file to ensure it is a valid ArgoCD Application and extract relevant fields.
4. For each Application, found in the directory, generate a JSON array element configuration that can be used to create a new ApplicationSet using a Git Generator.
5. Validate the generated JSON against a predefined JSON Schema.
6. In dry-run mode, output the generated JSON to the terminal without writing files.
7. In normal mode, write the generated JSON configuration to an output file.
8. Output migration statistics to the terminal.

## Architecture & Data Flow

- The CLI will use a pipeline pattern with components for scanning, parsing, migrating, and validating ArgoCD Application manifests.
- The Scanner module will recursively find ArgoCD Applications in `*.yaml`/`*.yml` files based on an input parameter specifying the directory.
- The Parser module will extract ArgoCD Application fields from YAML files.
- The Migrator module will generate JSON configs per ArgoCD Application.
- The Validator module will validate the generated JSON against a predefined JSON Schema using Draft7Validator

## Key Business Rules

- There should be a 1:1 mapping between ArgoCD Application YAML files and generated JSON configuration files.
- The CLI should skip any Application YAML files that are not valid ArgoCD Applications.

## Project To Do

- The TODO list for completing the implementation of this CLI tool is contained in the [TODO.md](TODO.md) file. When an item is completed, mark it as done by changing `[ ]` to `[x]`.
- TODO items will be exposed progressively as individual tasks to be completed. Additional details and requirements for each TODO item will be provided as needed.
- TODO items should be implemented using basic functionality, then add advanced options like custom output paths, logging levels, etc.
- Additional functionality should not be added until placed on the TODO list.
- Additional functionality may be added as the project evolves.
