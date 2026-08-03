#!/usr/bin/env bash
# Detects the mobile framework used at a given repo path.
# Usage: detect-framework.sh [path]   (defaults to ".")
# Prints one of: flutter | react-native | android
set -euo pipefail
ROOT="${1:-.}"

if [[ -f "$ROOT/pubspec.yaml" ]]; then
  echo "flutter"
  exit 0
fi

if [[ -f "$ROOT/package.json" ]] && [[ -d "$ROOT/android" ]] && grep -q '"react-native"' "$ROOT/package.json" 2>/dev/null; then
  echo "react-native"
  exit 0
fi

if [[ -f "$ROOT/build.gradle" || -f "$ROOT/build.gradle.kts" ]] || [[ -f "$ROOT/app/build.gradle" || -f "$ROOT/app/build.gradle.kts" ]]; then
  echo "android"
  exit 0
fi

echo "ERROR: Could not detect framework at '$ROOT'. Set 'framework:' explicitly in mobile-ci.yaml." >&2
exit 1
