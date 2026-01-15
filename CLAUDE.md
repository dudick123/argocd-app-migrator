# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A CLI tool that migrates ArgoCD Application YAML manifests to JSON configuration files for ApplicationSets using Git Generators.

**Migration Flow:**
1. ArgoCD Application YAML → 2. Parse & Extract → 3. JSON Config → 4. Validate → 5. Output

## Tech Stack

- **Python 3.12+** with UV package manager
- **CLI:** Typer with Rich for terminal output
- **Parsing:** PyYAML for YAML processing
- **Validation:** jsonschema (Draft7Validator)

## Project Structure

- `src/` - Main source code (use src layout)
- `tests/` - Pytest test cases
- `io-artifact-examples/` - Sample input/output files for testing:
  - `argocd-applications/` - Input: Application YAML files to migrate
  - `applicationset-generator-config/` - Output: Example JSON config format
  - `argocd-application-sets/` - Reference: ApplicationSet YAML examples
- `TODO.md` - Progressive task list (mark `[x]` when complete)

## Code Quality Requirements

- Files ≤ 300 lines, functions ≤ 50 lines
- Type hints required (enforce with mypy)
- Format with black, sort imports with isort, lint with flake8
- High test coverage with pytest
- No commits without: tests passing, linter clean, no secrets

## Architecture: Pipeline Pattern

The tool uses a 4-stage pipeline:

1. **Scanner** - Find `*.yaml`/`*.yml` files (recursive option available)
2. **Parser** - Extract fields from valid ArgoCD Applications, skip invalid files
3. **Migrator** - Transform to JSON config (1:1 mapping per Application)
4. **Validator** - Validate against JSON Schema (Draft7Validator)

### Input Example (ArgoCD Application)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: example-app
  annotations:
    argocd.argoproj.io/sync-wave: "40"
spec:
  project: default
  source:
    repoURL: https://github.com/org/repo.git
    targetRevision: main
    path: ./manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: default
```

### Output Example (JSON Config)
```json
[{
  "metadata": {
    "name": "example-app",
    "annotations": {"syncWave": "40"},
    "labels": {"environment": "dev", "team": "platform"}
  },
  "project": "default",
  "source": {
    "repoURL": "https://github.com/org/repo.git",
    "revision": "main",
    "manifestPath": "./manifests",
    "directory": {"recurse": true}
  },
  "destination": {
    "clusterName": "prod-cluster",
    "namespace": "default"
  },
  "enableSyncPolicy": false
}]
```

## CLI Modes

- **Dry-run mode:** Print JSON to terminal without writing files
- **Normal mode:** Write JSON files and show migration statistics

## Development Workflow

Tasks are tracked in [TODO.md](TODO.md):
- Mark completed tasks: `[ ]` → `[x]`
- Implement basic functionality first, then add advanced options
- Only add features listed in TODO.md
- New tasks will be added progressively as work continues
