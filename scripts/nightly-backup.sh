#!/bin/bash
# nightly-backup.sh
# Runs nightly at 04:00 AEDT to backup workspace and agent configs

set -euo pipefail
umask 077

WORKSPACE="/home/ubuntu/.openclaw/workspace"
BACKUP_DIR="/tmp/pandora-backup"
DATE=$(date +"%Y-%m-%d")
TIME=$(date +"%H:%M %Z")
BACKUP_REPO="https://github.com/Pandora-jk/pandora-backups.git"

echo "🌙 [${DATE} ${TIME}] Starting nightly backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup workspace
echo "📦 Backing up workspace..."
tar -czf "$BACKUP_DIR/workspace-$DATE.tar.gz" \
  --exclude='*.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  -C /home/ubuntu/.openclaw workspace

# Backup agent definitions
echo "📦 Backing up agent definitions..."
tar -czf "$BACKUP_DIR/agents-$DATE.tar.gz" \
  -C /home/ubuntu/.openclaw agents

# Calculate checksum
echo "🔐 Calculating checksums..."
sha256sum "$BACKUP_DIR/workspace-$DATE.tar.gz" > "$BACKUP_DIR/workspace-$DATE.tar.gz.sha256"
sha256sum "$BACKUP_DIR/agents-$DATE.tar.gz" > "$BACKUP_DIR/agents-$DATE.tar.gz.sha256"
chmod 600 "$BACKUP_DIR/workspace-$DATE.tar.gz" "$BACKUP_DIR/agents-$DATE.tar.gz" \
  "$BACKUP_DIR/workspace-$DATE.tar.gz.sha256" "$BACKUP_DIR/agents-$DATE.tar.gz.sha256"

# Keep a local latest workspace archive for integrity checks.
cp "$BACKUP_DIR/workspace-$DATE.tar.gz" /tmp/latest-workspace-backup.tar.gz
chmod 600 /tmp/latest-workspace-backup.tar.gz

# Get Bitwarden session for GitHub PAT
export BW_SESSION=$(bash /home/ubuntu/.openclaw/tools/bw-session.sh 2>/dev/null || echo "")
GH_PAT=$(bash /home/ubuntu/.openclaw/tools/bw-get.sh "github.com" password 2>/dev/null || echo "")

if [ -z "$GH_PAT" ]; then
  echo "⚠️  GitHub PAT not found, skipping GitHub upload"
else
  echo "☁️  Uploading to GitHub..."
  
  # Clone or pull backup repo
  if [ ! -d "$BACKUP_DIR/pandora-backups" ]; then
    git clone "https://$GH_PAT@github.com/Pandora-jk/pandora-backups.git" "$BACKUP_DIR/pandora-backups"
  else
    cd "$BACKUP_DIR/pandora-backups" && git pull
  fi
  
  # Copy backups to repo
  cp "$BACKUP_DIR"/*.tar.gz "$BACKUP_DIR/pandora-backups/"
  cp "$BACKUP_DIR"/*.sha256 "$BACKUP_DIR/pandora-backups/"
  
  # Commit and push
  cd "$BACKUP_DIR/pandora-backups"
  git add .
  git commit -m "Backup $DATE ${TIME}" || echo "No changes to commit"
  git push origin main
fi

# Cleanup local backup dir
rm -rf "$BACKUP_DIR"

echo "✅ Backup complete. Files uploaded to GitHub."
