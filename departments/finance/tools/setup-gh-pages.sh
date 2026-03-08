#!/bin/bash
# GitHub Pages Setup Script for Pandora Lead Qual Templates
# Run this after GitHub authentication is configured

set -e

REPO_NAME="pandora-leadqual-templates"
BRANCH="main"
TARGET_DIR="/home/ubuntu/.openclaw/workspace/departments/finance/templates"

echo "🔧 Setting up GitHub Pages for Pandora Lead Qual Templates..."
echo ""

# Check if GitHub is authenticated
if ! gh auth status &>/dev/null; then
    echo "❌ GitHub not authenticated. Please run: gh auth login"
    exit 1
fi

# Check if repo exists, create if not
if gh repo view "$REPO_NAME" &>/dev/null; then
    echo "✅ Repository exists: $REPO_NAME"
else
    echo "📦 Creating repository: $REPO_NAME"
    gh repo create "$REPO_NAME" --public --description "Pandora Lead Qual Website Templates"
fi

# Clone repo if not already cloned
if [ ! -d "/tmp/$REPO_NAME" ]; then
    echo "📥 Cloning repository..."
    git clone "https://github.com/$(gh config get user.login)/$REPO_NAME.git" "/tmp/$REPO_NAME"
fi

cd "/tmp/$REPO_NAME"

# Copy templates
echo "📄 Copying templates..."
cp "$TARGET_DIR"/index.html .
cp "$TARGET_DIR"/website-*.html .

# Commit and push
git add .
if git diff --cached --quiet; then
    echo "✅ No changes to commit"
else
    git commit -m "Update website templates $(date -I)"
    git push origin "$BRANCH"
    echo "✅ Templates deployed to GitHub Pages"
fi

# Enable GitHub Pages if not already enabled
echo "🌐 Checking GitHub Pages status..."
gh api repos/$(gh config get user.login)/$REPO_NAME/pages --method GET &>/dev/null || {
    echo "📢 Enabling GitHub Pages..."
    gh api repos/$(gh config get user.login)/$REPO_NAME/pages --method POST \
        -f source='{"branch":"main","path":"/"}'
}

echo ""
echo "✅ Setup complete!"
echo "🌐 Your templates are now live at: https://$(gh config get user.login).github.io/$REPO_NAME/"
echo ""
echo "Next steps:"
echo "1. Add the GitHub Pages URL to your Lead Qual cold email pitch"
echo "2. Share the demo links with potential customers"
echo "3. Monitor traffic via GitHub Analytics"
