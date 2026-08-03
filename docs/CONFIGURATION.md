# Configuration Reference

The pipeline is entirely driven by `mobile-ci.yaml` at the repo root,
validated on every run against `schemas/mobile-ci.schema.json` by the
`validate-config` action. If validation fails, the pipeline stops before
any build or deploy step runs.

| Field | Type | Purpose |
|---|---|---|
| `framework` | `auto\|flutter\|react-native\|android` | `auto` runs `scripts/detect-framework.sh` |
| `monorepo.enabled` / `monorepo.apps[]` | bool / list | Fans every workflow out into a per-app build matrix |
| `environments.<name>.branch` | string (glob) | Which branch pattern maps to this environment |
| `environments.<name>.android.*` | object | Per-environment applicationId / backend URL / Firebase project |
| `environments.<name>.featureFlags.*` | object | Remote-config provider + output file for that environment |
| `android.playstore.rollout.initial` | int (1-100) | Starting % for a production staged rollout |
| `quality.coverage.threshold` | int (0-100) | Minimum line coverage % required to deploy |
| `security.dependency_scan` / `secret_scan` | bool | Toggle the corresponding gate in the `security` action |
| `testing.visual_regression.*` | object | Chromatic/Percy integration toggle |
| `testing.performance_regression.*` | object | Artifact-size (or custom metric) regression budget |
| `changelog.enabled` | bool | Whether `release.yml` generates/commits a changelog entry |
| `dependencies.provider` | `renovate\|dependabot` | Which bot config is authoritative (see `renovate.json` / `.github/dependabot.yml`) |
| `notifications.slack.*` / `notifications.email.*` | object | Notification channels, gated independently |

See `schemas/mobile-ci.schema.json` for the authoritative, machine-checked
definition — this table is a human-readable summary of it.
