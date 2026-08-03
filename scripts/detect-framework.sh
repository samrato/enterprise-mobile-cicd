#!/usr/bin/env bash
# Detects the mobile framework used at a given repo path.
# Usage: detect-framework.sh [path]   (defaults to ".")
# Prints one of: flutter | react-native | android | monorepo
set -euo pipefail
ROOT="${1:-.}"

# 1. Check if mobile-ci.yaml exists and has explicit framework or monorepo settings
CONFIG_FILE="$ROOT/mobile-ci.yaml"
if [[ ! -f "$CONFIG_FILE" && -f "$ROOT/templates/mobile-ci.yaml" ]]; then
  CONFIG_FILE="$ROOT/templates/mobile-ci.yaml"
fi

if [[ -f "$CONFIG_FILE" ]]; then
  FRAMEWORK_CFG=$(grep -E '^\s*framework:' "$CONFIG_FILE" | head -n 1 | awk '{print $2}' | tr -d '"' | tr -d "'" || true)
  if [[ -n "$FRAMEWORK_CFG" && "$FRAMEWORK_CFG" != "auto" ]]; then
    echo "$FRAMEWORK_CFG"
    exit 0
  fi

  IS_MONOREPO=$(grep -A 2 -E '^\s*monorepo:' "$CONFIG_FILE" | grep -E '^\s*enabled:\s*true' || true)
  if [[ -n "$IS_MONOREPO" ]]; then
    echo "android" # Monorepo apps handle per-app framework in matrix
    exit 0
  fi
fi

# 2. File marker checks for auto-detection
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

# 3. Fallback for template repository testing or unconfigured repos
if [[ -f "$ROOT/templates/mobile-ci.yaml" || -d "$ROOT/examples" ]]; then
  echo "android"
  exit 0
fi

echo "ERROR: Could not detect framework at '$ROOT'. Set 'framework:' explicitly in mobile-ci.yaml (e.g., 'framework: flutter', 'framework: react-native', or 'framework: android')." >&2
exit 1


