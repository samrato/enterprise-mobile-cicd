#!/usr/bin/env bash
# Generates CHANGELOG.md content from conventional commits since the last tag.
# Usage: generate-changelog.sh <new-version> [prefix]
set -euo pipefail
NEW_VERSION="${1:?Usage: generate-changelog.sh <new-version> [prefix]}"
PREFIX="${2:-v}"

LAST_TAG=$(git describe --tags --match "${PREFIX}*" --abbrev=0 2>/dev/null || true)
RANGE="HEAD"
[[ -n "$LAST_TAG" ]] && RANGE="${LAST_TAG}..HEAD"

FEATS=$(git log $RANGE --pretty=format:'%s' | grep -E '^feat(\(.+\))?:' || true)
FIXES=$(git log $RANGE --pretty=format:'%s' | grep -E '^fix(\(.+\))?:' || true)
BREAKING=$(git log $RANGE --pretty=format:'%s%n%b' | grep -E 'BREAKING CHANGE' || true)
OTHERS=$(git log $RANGE --pretty=format:'%s' | grep -vE '^(feat|fix)(\(.+\))?:' || true)

DATE=$(date -u +%Y-%m-%d)

{
  echo "## ${PREFIX}${NEW_VERSION} — ${DATE}"
  echo ""
  if [[ -n "$BREAKING" ]]; then
    echo "### ⚠ Breaking Changes"
    echo "$BREAKING" | sed 's/^/- /'
    echo ""
  fi
  if [[ -n "$FEATS" ]]; then
    echo "### Features"
    echo "$FEATS" | sed -E 's/^feat(\(.+\))?: /- /'
    echo ""
  fi
  if [[ -n "$FIXES" ]]; then
    echo "### Fixes"
    echo "$FIXES" | sed -E 's/^fix(\(.+\))?: /- /'
    echo ""
  fi
  if [[ -n "$OTHERS" ]]; then
    echo "### Other Changes"
    echo "$OTHERS" | sed 's/^/- /'
    echo ""
  fi
} | tee /tmp/changelog-entry.md

echo "---"
echo "Wrote entry to /tmp/changelog-entry.md"
