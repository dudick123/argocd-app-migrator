# Quick Start Guide

## Installation

1. Clone the repository:
```bash
git clone https://github.com/dudick123/argocd-app-migrator.git
cd argocd-app-migrator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Make the script executable (optional):
```bash
chmod +x migrate.py
```

## Quick Test

Validate the example files:
```bash
python migrate.py validate ./examples/
```

Try a dry run:
```bash
python migrate.py migrate ./examples/ \
  --config-repo https://dev.azure.com/myorg/myproject/_git/gitops \
  --dry-run
```

## First Migration

1. Put your ApplicationSet YAML files in a directory
2. Run validation:
```bash
python migrate.py validate /path/to/applicationsets/
```

3. Run migration:
```bash
python migrate.py migrate /path/to/applicationsets/ \
  --config-repo https://your-repo-url
```

## With Azure DevOps

Set environment variables:
```bash
export ADO_ORG=https://dev.azure.com/yourorg
export ADO_PROJECT=yourproject
export ADO_REPO=yourrepo
export ADO_PAT=your_pat_token
```

Run migration with PR creation:
```bash
python migrate.py migrate /path/to/applicationsets/ \
  --config-repo https://dev.azure.com/yourorg/yourproject/_git/yourrepo \
  --create-pr
```

## Next Steps

- Read the full [README.md](README.md) for detailed usage
- Check [examples/](examples/) for sample files
- Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Getting Help

- Open an issue on GitHub
- Check existing issues for solutions
- Review the troubleshooting section in README.md
