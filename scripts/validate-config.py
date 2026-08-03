#!/usr/bin/env python3
"""
Validates a mobile-ci.yaml file against schemas/mobile-ci.schema.json.
Usage: validate-config.py <path-to-mobile-ci.yaml> <path-to-schema.json>
Exits non-zero with a readable error list on failure.
"""
import sys
import json

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema is required (pip install jsonschema)", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: validate-config.py <mobile-ci.yaml> <schema.json>", file=sys.stderr)
        return 2

    config_path, schema_path = sys.argv[1], sys.argv[2]

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    with open(schema_path, "r") as f:
        schema = json.load(f)

    validator = jsonschema.Draft7Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: e.path)

    if errors:
        print(f"::error::mobile-ci.yaml failed validation ({len(errors)} issue(s)):")
        for err in errors:
            location = ".".join(str(p) for p in err.path) or "<root>"
            print(f"  - {location}: {err.message}")
        return 1

    # Cross-field sanity checks beyond what JSON Schema conveniently expresses
    warnings = []
    if config.get("monorepo", {}).get("enabled") and not config.get("monorepo", {}).get("apps"):
        errors_extra = "monorepo.enabled is true but monorepo.apps is empty"
        print(f"::error::{errors_extra}")
        return 1

    if config.get("ios", {}).get("enabled") and "production" in config.get("environments", {}):
        if not config["environments"]["production"].get("ios", {}).get("bundleId"):
            warnings.append("ios.enabled is true but environments.production.ios.bundleId is not set")

    for w in warnings:
        print(f"::warning::{w}")

    print("mobile-ci.yaml is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
