#!/usr/bin/env bash
# Shreds and removes any temporary secret material written under
# $RUNNER_TEMP during the build (keystore, provisioning profiles, etc).
set -euo pipefail
TARGET_DIR="${1:-$RUNNER_TEMP}"

if [[ -z "${TARGET_DIR:-}" || ! -d "$TARGET_DIR" ]]; then
  echo "Nothing to clean (no temp dir)."
  exit 0
fi

for pattern in "keystore" "profiles" "*.p12" "*.mobileprovision" "*.jks" "*.keystore"; do
  find "$TARGET_DIR" -name "$pattern" -print0 2>/dev/null | while IFS= read -r -d '' f; do
    if command -v shred >/dev/null 2>&1; then
      shred -u "$f" || rm -f "$f"
    else
      rm -f "$f"
    fi
    echo "cleaned: $f"
  done
done
