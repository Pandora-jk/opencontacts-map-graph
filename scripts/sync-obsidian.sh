#!/bin/bash
# sync-obsidian.sh
# Auto-syncs entire workspace to Obsidian vault every 10 minutes

VAULT_DIR="/tmp/pandora-obsidian-vault"
WORKSPACE="/home/ubuntu/.openclaw"
GH_USER="Pandora-jk"
GH_REPO="pandora-obsidian-vault"

# Get GitHub PAT from Bitwarden
export BW_SESSION=$(bash tools/bw-session.sh 2>/dev/null || echo "")
GH_PAT=$(bash tools/bw-get.sh "github.com" password 2>/dev/null || echo "")

if [ -z "$GH_PAT" ]; then
  echo "⚠️  GitHub PAT not found. Skipping sync."
  exit 1
fi

cd "$VAULT_DIR" || exit 1

# Pull latest changes from GitHub (in case phone edited something)
git pull origin main --ff-only || echo "⚠️  Pull failed, continuing with push"

# Copy updated files from workspace
echo "📥 Syncing agent definitions..."
cp "$WORKSPACE/agents/"*.md "$VAULT_DIR/" 2>/dev/null || true

echo "📥 Syncing workspace files..."
cp "$WORKSPACE/workspace/"*.md "$VAULT_DIR/" 2>/dev/null || true

# Copy department files (flattened)
cp "$WORKSPACE/workspace/departments/"*/*.md "$VAULT_DIR/" 2>/dev/null || true

# Copy logs
mkdir -p "$VAULT_DIR/logs"
cp "$WORKSPACE/workspace/logs/"*.md "$VAULT_DIR/logs/" 2>/dev/null || true

# Check for changes
if [ -n "$(git status --porcelain)" ]; then
  echo "📝 Changes detected..."
  
  # Add and commit
  git add .
  git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')"
  
  # Push to GitHub
  git remote set-url origin "https://$GH_USER:$GH_PAT@github.com/$GH_USER/$GH_REPO.git"
  git push -u origin main
  
  echo "✅ Synced to GitHub at $(date)"
else
  echo "✅ No changes to sync at $(date)"
fi
