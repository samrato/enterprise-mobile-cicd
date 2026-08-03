# Monitoring

Each workflow run naturally produces the raw signal for these metrics via
the GitHub Actions API / step summaries. The platform doesn't ship a
dashboard (that's specific to your org's stack), but it emits what you
need to build one:

| Metric | Where it comes from |
|---|---|
| Build duration | GitHub Actions job timing (`GET /repos/{owner}/{repo}/actions/runs`) |
| Test duration | Same — per-step timing on the `test` action's steps |
| Cache hit rate | `actions/cache`'s own run summary (`Cache restored from key: ...` vs `Cache not found`) |
| Coverage % | Written to `$GITHUB_STEP_SUMMARY` by the `coverage` action on every run |
| Deployment frequency | Count of successful `deploy-*.yml` runs over time |
| Failure rate | Count of failed runs / total runs, per workflow |
| Rollback frequency | Count of `rollback.yml` dispatches |
| Mean time to recovery | Time between a failed `deploy-prod.yml` run and the next successful one |

To centralize these, the simplest approach is a small scheduled workflow
that calls the GitHub REST API for workflow run history and pushes the
result to your metrics store (Datadog, Grafana Cloud, BigQuery, etc.) —
intentionally left out of this platform since the destination is
org-specific. `monitoring.track_metrics: true` in `mobile-ci.yaml` is a
forward-compatible flag for that future action.
