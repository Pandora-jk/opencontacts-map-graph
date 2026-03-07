#!/usr/bin/env bash
# verify-backup-integrity.sh
# Integrity checks for workspace backup archives with optional permission hardening.

set -euo pipefail
umask 077

ARCHIVE=""
SOURCE="/home/ubuntu/.openclaw/workspace/INCOME-ENGINE.md"
ENFORCE_PERMISSIONS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive)
      ARCHIVE="${2:-}"
      shift 2
      ;;
    --source)
      SOURCE="${2:-}"
      shift 2
      ;;
    --enforce-permissions)
      ENFORCE_PERMISSIONS=1
      shift
      ;;
    *)
      echo "WARN: unknown arg '$1' ignored"
      shift
      ;;
  esac
done

if [[ -z "$ARCHIVE" ]]; then
  if compgen -G "/tmp/pandora-backup/workspace-*.tar.gz" > /dev/null; then
    ARCHIVE="$(ls -1t /tmp/pandora-backup/workspace-*.tar.gz | head -n1)"
  fi
fi

if [[ -z "$ARCHIVE" ]]; then
  echo "WARN: backup archive not found. Provide --archive or configure local backup retention."
  exit 0
fi

if [[ ! -r "$ARCHIVE" ]]; then
  echo "FAIL: backup archive is not readable: $ARCHIVE"
  exit 0
fi

if ! tar -tzf "$ARCHIVE" >/dev/null 2>&1; then
  echo "FAIL: archive is corrupt or unreadable: $ARCHIVE"
  exit 0
fi

target_rel="${SOURCE#/home/ubuntu/.openclaw/}"
target_no_slash="${SOURCE#/}"
members="$(tar -tzf "$ARCHIVE")"

if printf '%s\n' "$members" | grep -Eq '^/|(^|/)\.\.(/|$)'; then
  echo "FAIL: archive contains unsafe absolute or parent-path entries"
  exit 0
fi

if find "$ARCHIVE" -maxdepth 0 -perm /077 -print -quit 2>/dev/null | grep -q .; then
  if [[ "$ENFORCE_PERMISSIONS" -eq 1 ]]; then
    if chmod 600 "$ARCHIVE" 2>/dev/null; then
      echo "FIXED: backup archive permissions hardened to 600: $ARCHIVE"
    else
      echo "RISK: backup archive is readable by group/other; unable to enforce chmod 600"
    fi
  else
    echo "RISK: backup archive is readable by group/other; tighten permissions (chmod 600)"
  fi
fi

member=""
if printf '%s\n' "$members" | grep -qx "workspace/INCOME-ENGINE.md"; then
  member="workspace/INCOME-ENGINE.md"
elif printf '%s\n' "$members" | grep -qx "$target_rel"; then
  member="$target_rel"
elif printf '%s\n' "$members" | grep -qx "$target_no_slash"; then
  member="$target_no_slash"
else
  member="$(printf '%s\n' "$members" | grep -E '(^|/)INCOME-ENGINE\.md$' | head -n1 || true)"
fi

if [[ -z "$member" ]]; then
  echo "FAIL: source file not found in archive: ${SOURCE}"
  exit 0
fi

if [[ ! -f "$SOURCE" ]]; then
  echo "WARN: source file missing on disk; archive structure passed: $member"
  echo "PASS: archive readable and target present: $ARCHIVE"
  exit 0
fi

tmp_file="$(mktemp)"
trap 'rm -f "$tmp_file"' EXIT

if ! tar -xOf "$ARCHIVE" "$member" > "$tmp_file" 2>/dev/null; then
  echo "FAIL: unable to extract target member from archive: $member"
  exit 0
fi

src_sha="$(sha256sum "$SOURCE" | awk '{print $1}')"
bak_sha="$(sha256sum "$tmp_file" | awk '{print $1}')"

if [[ "$src_sha" == "$bak_sha" ]]; then
  echo "PASS: backup integrity verified ($member)"
  echo "Archive: $ARCHIVE"
  echo "SHA256: $bak_sha"
else
  echo "RISK: backup differs from current source ($member)"
  echo "Archive: $ARCHIVE"
  echo "Archive SHA256: $bak_sha"
  echo "Source  SHA256: $src_sha"
fi
