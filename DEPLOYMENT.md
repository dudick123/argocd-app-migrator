# Deployment Guide

## Files Created

Your ArgoCD ApplicationSet Migrator project includes:

### Core Files
- `migrate.py` - Main CLI application (executable)
- `requirements.txt` - Python dependencies
- `commit_to_github.sh` - Helper script to commit to GitHub (executable)

### Documentation
- `README.md` - Comprehensive usage documentation
- `QUICKSTART.md` - Quick start guide
- `CONTRIBUTING.md` - Contribution guidelines
- `LICENSE` - MIT License

### Examples
- `examples/scm-applicationset.yaml` - Example SCM-based ApplicationSet
- `examples/git-applicationset.yaml` - Example Git generator ApplicationSet
- `examples/applications.json` - Example JSON data structure

### Configuration
- `.gitignore` - Git ignore rules

## Deployment Steps

### Step 1: Clone and Setup on Your Local Machine

```bash
# Navigate to where you want the project
cd ~/projects

# Clone your repository
git clone https://github.com/dudick123/argocd-app-migrator.git
cd argocd-app-migrator

# Copy the downloaded files from Claude into this directory
# (Download the argocd-app-migrator folder from the outputs)
```

### Step 2: Initialize Git and Create Branch

```bash
# If starting fresh, initialize git
git init
git remote add origin https://github.com/dudick123/argocd-app-migrator.git

# Create and checkout feature branch
git checkout -b feature/initial-implementation

# Stage all files
git add .

# Commit
git commit -m "feat: initial implementation of ApplicationSet migrator

- Add CLI tool for migrating ApplicationSets from SCM to Git generators
- Implement Azure DevOps integration for automated PR creation
- Add validation and dry-run modes
- Include comprehensive documentation and examples
- Add MIT license and contributing guidelines"
```

### Step 3: Push to GitHub

```bash
# Push the feature branch
git push -u origin feature/initial-implementation
```

### Step 4: Create Pull Request

1. Go to https://github.com/dudick123/argocd-app-migrator
2. You'll see a prompt to create a PR for your new branch
3. Click "Compare & pull request"
4. Add a description (use the commit message)
5. Create the pull request
6. Review and merge into main

### Step 5: Test Installation

After merging to main:

```bash
# Clone the main branch
git clone https://github.com/dudick123/argocd-app-migrator.git
cd argocd-app-migrator

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test with examples
python migrate.py validate ./examples/

# Test dry run
python migrate.py migrate ./examples/ \
  --config-repo https://example.com/repo.git \
  --dry-run
```

## Alternative: Using the Helper Script

If you're in the project directory with all files:

```bash
# Make the script executable (if not already)
chmod +x commit_to_github.sh

# Run the helper script
./commit_to_github.sh

# Then push
git push -u origin feature/initial-implementation
```

## Next Steps After Deployment

1. **Create a GitHub Release**
   - Tag: `v1.0.0`
   - Title: "Initial Release"
   - Description: Summary of features

2. **Update Repository Settings**
   - Add description: "CLI tool for migrating ArgoCD ApplicationSets from SCM to Git generators"
   - Add topics: `argocd`, `kubernetes`, `gitops`, `cli`, `azure-devops`

3. **Share with Your Team**
   - Send repository link
   - Share QUICKSTART.md
   - Provide example usage

4. **Test with Real Data**
   - Run on your actual ApplicationSet files
   - Validate the migration output
   - Test Azure DevOps integration

## Troubleshooting Deployment

### Permission Denied on Git Push

If you get permission denied:

```bash
# Use HTTPS with token
git remote set-url origin https://YOUR_GITHUB_TOKEN@github.com/dudick123/argocd-app-migrator.git

# Or use SSH (if you have SSH keys set up)
git remote set-url origin git@github.com:dudick123/argocd-app-migrator.git
```

### Branch Already Exists

If the branch already exists:

```bash
# Delete remote branch
git push origin --delete feature/initial-implementation

# Delete local branch
git branch -D feature/initial-implementation

# Start fresh
git checkout -b feature/initial-implementation
```

### Files Not Showing Up

Ensure all files are staged:

```bash
git status
git add .
git commit -m "your message"
```

## GitHub Personal Access Token

If using HTTPS, create a token at:
https://github.com/settings/tokens

Required scopes:
- `repo` (Full control of private repositories)

Use the token as your password when pushing.

## Questions?

- Check README.md for full documentation
- Review QUICKSTART.md for quick setup
- Open an issue on GitHub for help
