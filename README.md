# ArgoCD ApplicationSet Migrator

A CLI utility to migrate ArgoCD ApplicationSets from SCM generators to Git generators with JSON data structures.

## Overview

This tool helps teams transition from SCM-based ApplicationSet generators (GitHub, GitLab, Bitbucket) to Git file-based generators using a centralized JSON data structure. This pattern provides:

- **Explicit configuration**: All application parameters in a single, versioned JSON file
- **Better control**: No dependency on external SCM provider APIs
- **Simplified auditing**: Clear history of application changes through Git commits
- **Easier templating**: Direct parameter substitution from JSON structure

## Features

- ✅ Batch migration of ApplicationSet YAML files
- ✅ Automatic JSON data structure generation
- ✅ Template transformation with parameter substitution
- ✅ Validation and dry-run modes
- ✅ Azure DevOps integration for PR creation
- ✅ Rich CLI output with progress tracking
- ✅ Error handling and detailed reporting

## Installation

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install typer rich pyyaml azure-devops
```

## Usage

### Validate ApplicationSets

Preview which ApplicationSets use SCM generators before migrating:

```bash
python migrate.py validate ./applicationsets/
```

Output shows:
- File names
- Kind (ApplicationSet, other)
- Whether it uses SCM generators
- Template name

### Basic Migration (Local Files)

Migrate ApplicationSets and create local files:

```bash
python migrate.py migrate ./applicationsets/ \
  --config-repo https://dev.azure.com/myorg/myproject/_git/gitops-config
```

This will:
1. Process all YAML files in the directory
2. Extract template data from SCM-based ApplicationSets
3. Generate a JSON data file (`applications.json`)
4. Create transformed ApplicationSet YAMLs in `./applicationsets/migrated/`

### Migration with Custom Paths

Specify custom output locations and JSON paths:

```bash
python migrate.py migrate ./applicationsets/ \
  --config-repo https://dev.azure.com/myorg/myproject/_git/gitops-config \
  --json-output ./config/apps.json \
  --json-path config/applications.json \
  --output-dir ./transformed
```

### Dry Run

Preview changes without creating files:

```bash
python migrate.py migrate ./applicationsets/ \
  --config-repo https://dev.azure.com/myorg/myproject/_git/gitops-config \
  --dry-run
```

### Azure DevOps Integration

Create a pull request with migrated files automatically:

```bash
python migrate.py migrate ./applicationsets/ \
  --config-repo https://dev.azure.com/myorg/myproject/_git/gitops-config \
  --create-pr \
  --ado-org https://dev.azure.com/myorg \
  --ado-project myproject \
  --ado-repo gitops-config \
  --ado-pat $ADO_PAT
```

Or use environment variables:

```bash
export ADO_ORG=https://dev.azure.com/myorg
export ADO_PROJECT=myproject
export ADO_REPO=gitops-config
export ADO_PAT=your_personal_access_token

python migrate.py migrate ./applicationsets/ \
  --config-repo https://dev.azure.com/myorg/myproject/_git/gitops-config \
  --create-pr
```

### Advanced Options

```bash
python migrate.py migrate ./applicationsets/ \
  --config-repo https://dev.azure.com/myorg/myproject/_git/gitops-config \
  --create-pr \
  --branch feature/appset-migration-phase1 \
  --target-branch main \
  --pr-title "feat: migrate core apps to git generator" \
  --json-path applicationsets/production.json \
  --appsets-path manifests/applicationsets \
  --all  # Process all ApplicationSets, not just SCM-based ones
```

## Command Reference

### `migrate`

Migrate ApplicationSets from SCM to Git generators.

**Arguments:**
- `input_dir` - Directory containing ApplicationSet YAML files (required)

**Options:**
- `--output-dir, -o` - Output directory for transformed ApplicationSets (default: `input_dir/migrated`)
- `--json-output, -j` - Output path for JSON data file (default: `applications.json`)
- `--config-repo, -r` - Git repository URL where JSON will be stored (required)
- `--json-path` - Path to JSON file within the config repo (default: `applicationsets/data.json`)
- `--appsets-path` - Path for ApplicationSet manifests in repo (default: `applicationsets/manifests`)
- `--dry-run` - Preview changes without writing files
- `--scm-only/--all` - Filter SCM-only or process all ApplicationSets (default: `--scm-only`)

**Azure DevOps Options:**
- `--create-pr` - Create a pull request in Azure DevOps
- `--ado-org` - Azure DevOps organization URL (env: `ADO_ORG`)
- `--ado-project` - Azure DevOps project name (env: `ADO_PROJECT`)
- `--ado-repo` - Azure DevOps repository name (env: `ADO_REPO`)
- `--ado-pat` - Azure DevOps Personal Access Token (env: `ADO_PAT`)
- `--branch` - Branch name for migration (default: `feature/migrate-applicationsets-to-git-generator`)
- `--target-branch` - Target branch for PR (default: `main`)
- `--pr-title` - Custom PR title
- `--pr-description` - Custom PR description

### `validate`

Validate ApplicationSet files and show SCM generator usage.

**Arguments:**
- `input_dir` - Directory containing ApplicationSet YAML files (required)

## Azure DevOps Setup

### Personal Access Token (PAT)

Your PAT needs these scopes:
- **Code**: Read & Write
- **Pull Request Threads**: Read & Write

Create a PAT at: `https://dev.azure.com/{org}/_usersSettings/tokens`

### Environment Variables

For convenience, set these in your shell profile:

```bash
# ~/.bashrc or ~/.zshrc
export ADO_ORG=https://dev.azure.com/myorg
export ADO_PROJECT=myproject
export ADO_REPO=gitops-config
export ADO_PAT=your_pat_here
```

## Migration Pattern

### Before (SCM Generator)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-apps
spec:
  generators:
    - scmProvider:
        github:
          organization: myorg
          cloneProtocol: https
  template:
    metadata:
      name: '{{repository}}'
    spec:
      project: default
      source:
        repoURL: '{{url}}'
        targetRevision: '{{branch}}'
        path: manifests
```

### After (Git Generator)

**ApplicationSet:**
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-apps
spec:
  generators:
    - git:
        repoURL: https://dev.azure.com/myorg/myproject/_git/gitops-config
        revision: HEAD
        files:
          - path: applicationsets/data.json
  template:
    metadata:
      name: '{{name}}'
    spec:
      project: '{{project}}'
      source:
        repoURL: '{{repoUrl}}'
        targetRevision: '{{targetRevision}}'
        path: '{{path}}'
```

**JSON Data Structure:**
```json
{
  "applications": [
    {
      "name": "app1",
      "project": "default",
      "path": "manifests/app1",
      "repoUrl": "https://github.com/myorg/app1",
      "targetRevision": "main"
    },
    {
      "name": "app2",
      "project": "platform",
      "path": "k8s/base",
      "repoUrl": "https://github.com/myorg/app2",
      "targetRevision": "main"
    }
  ]
}
```

## Examples

### Example 1: Simple Migration

```bash
# Validate first
python migrate.py validate ./my-applicationsets/

# Dry run
python migrate.py migrate ./my-applicationsets/ \
  --config-repo https://dev.azure.com/acme/platform/_git/gitops \
  --dry-run

# Actual migration
python migrate.py migrate ./my-applicationsets/ \
  --config-repo https://dev.azure.com/acme/platform/_git/gitops
```

### Example 2: Multi-Environment Migration

```bash
# Development
python migrate.py migrate ./applicationsets/dev/ \
  --config-repo https://dev.azure.com/acme/platform/_git/gitops \
  --json-path config/dev/applications.json \
  --output-dir ./migrated/dev

# Staging
python migrate.py migrate ./applicationsets/staging/ \
  --config-repo https://dev.azure.com/acme/platform/_git/gitops \
  --json-path config/staging/applications.json \
  --output-dir ./migrated/staging

# Production
python migrate.py migrate ./applicationsets/prod/ \
  --config-repo https://dev.azure.com/acme/platform/_git/gitops \
  --json-path config/prod/applications.json \
  --output-dir ./migrated/prod
```

### Example 3: Automated PR Creation

```bash
# Set credentials once
export ADO_ORG=https://dev.azure.com/acme
export ADO_PROJECT=platform
export ADO_REPO=gitops
export ADO_PAT=$(cat ~/.ado-pat)

# Migrate with PR
python migrate.py migrate ./applicationsets/ \
  --config-repo https://dev.azure.com/acme/platform/_git/gitops \
  --create-pr \
  --branch feature/migrate-to-git-generators \
  --pr-title "chore: migrate ApplicationSets to Git generator pattern"
```

## Troubleshooting

### "No YAML files found"

Ensure your directory contains `.yaml` or `.yml` files:
```bash
ls -la ./applicationsets/*.{yaml,yml}
```

### "Not using SCM generator"

By default, only SCM-based ApplicationSets are processed. Use `--all` to process all ApplicationSets:
```bash
python migrate.py migrate ./applicationsets/ \
  --config-repo <url> \
  --all
```

### Azure DevOps Authentication Errors

Verify your PAT:
- Has not expired
- Has correct scopes (Code: Read & Write, Pull Request Threads: Read & Write)
- Organization URL is correct format: `https://dev.azure.com/orgname`

### Branch Already Exists

The tool will use existing branches. Delete the branch first if you want a fresh start:
```bash
# In Azure DevOps, delete the branch via UI or CLI
az repos ref delete --name refs/heads/feature/migrate-applicationsets-to-git-generator \
  --object-id $(az repos ref list --query "[?name=='refs/heads/feature/migrate-applicationsets-to-git-generator'].objectId | [0]" -o tsv) \
  --repository gitops-config \
  --project myproject \
  --organization https://dev.azure.com/myorg
```

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section

## Roadmap

- [ ] GitHub integration for PR creation
- [ ] GitLab integration for MR creation
- [ ] Support for matrix generators
- [ ] Rollback command
- [ ] Diff preview before migration
- [ ] Multi-file JSON support (one per environment)
- [ ] Integration tests
