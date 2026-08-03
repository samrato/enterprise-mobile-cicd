#!/usr/bin/env python3
"""
Reads mobile-ci.yaml and emits a GitHub Actions matrix (JSON) describing
each app to build. If monorepo is disabled, emits a single-entry matrix
representing the repo root, so downstream workflow steps can always assume
a matrix exists (uniform code path for single-app and monorepo cases).

Usage: monorepo-matrix.py <mobile-ci.yaml>
Output: matrix=<json> written to stdout in "key=value" form for $GITHUB_OUTPUT
"""
import json
import sys

import yaml


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: monorepo-matrix.py <mobile-ci.yaml>", file=sys.stderr)
        return 2

    with open(sys.argv[1]) as f:
        config = yaml.safe_load(f)

    mono = config.get("monorepo", {})
    if mono.get("enabled"):
        apps = mono.get("apps", [])
        if not apps:
            print("ERROR: monorepo.enabled is true but no apps are defined", file=sys.stderr)
            return 1
        include = [
            {
                "name": app["name"],
                "path": app["path"],
                "framework": app.get("framework", config.get("framework", "auto")),
            }
            for app in apps
        ]
    else:
        include = [
            {
                "name": "app",
                "path": ".",
                "framework": config.get("framework", "auto"),
            }
        ]

    matrix = {"include": include}
    print(f"matrix={json.dumps(matrix)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
