#!/bin/bash
# sync-logseq.sh
# Auto-syncs Logseq vault to GitHub every 10 minutes
# Run via cron: */10 * * * * /home/ubuntu/.openclaw/workspace/core/sync-logseq.sh

VAULT_DIR="/tmp/logseq-vault"
WORKSPACE="/home/ubuntu/.openclaw/workspace"
BW_SESSION_CMD="bash tools/bw-session.sh >/dev/null 2>&1"
GH_USER="Pandora-jk"

# Refresh Bitwarden session
eval $BW_SESSION_CMD
GH_PAT=$(bash tools/bw-get.sh "github.com" password 2>/dev/null)

cd "$VAULT_DIR" || exit 1

# Check for changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Changes detected in Logseq vault..."
    
    # Add and commit
    git add .
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M')"
    
    # Push
    git remote set-url origin "https://$GH_USER:$GH_PAT@github.com/$GH_USER/pandora-van-life-logs.git"
    git push -f origin main
    
    echo "✅ Synced to GitHub at $(date)"
else
    echo "✅ No changes to sync at $(date)"
fi

# Pull any changes from mobile (if you edited on phone)
git pull origin main --ff-only 2>/dev/null || echo "⚠️ No new changes from remote"
