#!/usr/bin/env python3
"""
Lightweight performance-regression gate.

Compares a current build metric (e.g. artifact size in bytes) against a
baseline stored in the GitHub Actions cache (baseline.json, restored/saved
by the performance-regression action). Fails if the regression exceeds the
configured budget percentage.

Usage: check-perf-budget.py --current <bytes> --baseline-file <path> \
                             --budget-percent <float> --metric apk_size
On first run (no baseline file yet), it writes the current value as the
baseline and passes.
"""
import argparse
import json
import os
import sys


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--current", type=float, required=True)
    p.add_argument("--baseline-file", required=True)
    p.add_argument("--budget-percent", type=float, default=10.0)
    p.add_argument("--metric", default="apk_size")
    args = p.parse_args()

    baseline_value = None
    if os.path.exists(args.baseline_file):
        with open(args.baseline_file) as f:
            data = json.load(f)
        baseline_value = data.get(args.metric)

    if baseline_value is None:
        with open(args.baseline_file, "w") as f:
            json.dump({args.metric: args.current}, f)
        print(f"No baseline found for '{args.metric}'. Recorded {args.current} as the new baseline.")
        return 0

    delta_percent = ((args.current - baseline_value) / baseline_value) * 100
    print(f"Baseline {args.metric}: {baseline_value}")
    print(f"Current  {args.metric}: {args.current}")
    print(f"Delta: {delta_percent:+.2f}% (budget: {args.budget_percent}%)")

    if delta_percent > args.budget_percent:
        print(f"::error::Performance regression: {args.metric} grew {delta_percent:.2f}%, "
              f"exceeding the {args.budget_percent}% budget.")
        return 1

    # Only ratchet the baseline down/forward on improvement or within-budget growth
    with open(args.baseline_file, "w") as f:
        json.dump({args.metric: args.current}, f)

    print("Within performance budget.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
