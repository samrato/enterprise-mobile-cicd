#!/usr/bin/env python3
"""
Computes the next semantic version from conventional-commit history since
the last tag, and a monotonically increasing build number (Android
versionCode-compatible: total commit count).

Usage: version-bump.py [--prefix v]
Outputs (to stdout, for $GITHUB_OUTPUT consumption by the calling action):
  version=<semver>
  build_number=<int>
Rules:
  - any commit with "BREAKING CHANGE" or "!" after type -> major bump
  - "feat:" -> minor bump
  - anything else ("fix:", "chore:", etc.) -> patch bump
  - no prior tag -> starts at 0.1.0
"""
import argparse
import re
import subprocess
import sys


def sh(cmd: str) -> str:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False).stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="v")
    args = parser.parse_args()

    last_tag = sh(f"git describe --tags --match '{args.prefix}*' --abbrev=0 2>/dev/null")
    build_number = sh("git rev-list --count HEAD") or "1"

    if not last_tag:
        version = "0.1.0"
        print(f"version={version}")
        print(f"build_number={build_number}")
        return 0

    match = re.match(rf"^{re.escape(args.prefix)}?(\d+)\.(\d+)\.(\d+)", last_tag)
    if not match:
        print(f"::warning::Could not parse last tag '{last_tag}', defaulting to 0.1.0", file=sys.stderr)
        version = "0.1.0"
        print(f"version={version}")
        print(f"build_number={build_number}")
        return 0

    major, minor, patch = (int(x) for x in match.groups())

    log = sh(f"git log {last_tag}..HEAD --pretty=format:%s%n%b")
    bump = "patch"
    for line in log.splitlines():
        if re.search(r"BREAKING CHANGE", line) or re.match(r"^\w+(\([\w.-]+\))?!:", line):
            bump = "major"
            break
        if re.match(r"^feat(\([\w.-]+\))?:", line) and bump != "major":
            bump = "minor"

    if bump == "major":
        major, minor, patch = major + 1, 0, 0
    elif bump == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1

    version = f"{major}.{minor}.{patch}"
    print(f"version={version}")
    print(f"build_number={build_number}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
