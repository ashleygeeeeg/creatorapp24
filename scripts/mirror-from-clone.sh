#!/usr/bin/env bash
# Copy the full application tree from Clone into your local creatorapp24 checkout.
set -euo pipefail
SRC="${1:-https://github.com/ashleygeeeeg/Clone.git}"
TMP="$(mktemp -d)"
git clone --depth 1 "$SRC" "$TMP/Clone"
rsync -a --delete "$TMP/Clone/frontend/" "$(dirname "$0")/../frontend/" 2>/dev/null || {
  echo "Install rsync or copy frontend/ manually from Clone"
  exit 1
}
echo "frontend/ synced from Clone. Review, commit, and: git push origin main"
