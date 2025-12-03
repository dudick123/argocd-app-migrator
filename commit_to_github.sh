#!/bin/bash

# Script to commit and push files to GitHub
# Usage: ./commit_to_github.sh

set -e

BRANCH_NAME="feature/initial-implementation"
REPO_URL="https://github.com/dudick123/argocd-app-migrator.git"

echo "🚀 ArgoCD App Migrator - GitHub Commit Helper"
echo "=============================================="
echo ""

# Check if we're already in a git repo
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git remote add origin "$REPO_URL"
else
    echo "✓ Git repository already initialized"
fi

echo ""
echo "🌿 Creating feature branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME" 2>/dev/null || git checkout "$BRANCH_NAME"

echo ""
echo "📝 Staging files..."
git add .

echo ""
echo "💾 Committing files..."
git commit -m "feat: initial implementation of ApplicationSet migrator

- Add CLI tool for migrating ApplicationSets from SCM to Git generators
- Implement Azure DevOps integration for automated PR creation
- Add validation and dry-run modes
- Include comprehensive documentation and examples
- Add MIT license and contributing guidelines"

echo ""
echo "📤 Ready to push to GitHub!"
echo ""
echo "To push the changes, run:"
echo "  git push -u origin $BRANCH_NAME"
echo ""
echo "Then create a pull request on GitHub to merge into main."
echo ""
echo "✅ Done!"
