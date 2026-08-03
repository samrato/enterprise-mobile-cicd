#!/usr/bin/env bash
# Decodes a base64 keystore secret into a temporary file on the runner's
# ephemeral tmpfs, and prints its path. The caller (signing action) is
# responsible for invoking cleanup.sh / cleanup action afterward.
set -euo pipefail

SECRET_B64="${1:?Usage: decode-keystore.sh <base64-secret> [output-dir]}"
OUT_DIR="${2:-$RUNNER_TEMP}"

if [[ -z "${OUT_DIR:-}" ]]; then
  echo "ERROR: no output dir provided and \$RUNNER_TEMP is unset" >&2
  exit 1
fi

mkdir -p "$OUT_DIR/keystore"
KEYSTORE_PATH="$OUT_DIR/keystore/release.keystore"

echo "$SECRET_B64" | base64 --decode > "$KEYSTORE_PATH"
chmod 600 "$KEYSTORE_PATH"

echo "$KEYSTORE_PATH"
