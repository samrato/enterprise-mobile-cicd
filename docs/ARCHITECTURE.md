# Architecture

## Why composite actions instead of one big workflow

Every pipeline stage — detect framework, install deps, lint, scan, test,
build, sign, deploy, notify, clean up — lives in its own directory under
`.github/actions/`, each with a single `action.yml`. Workflows
(`.github/workflows/*.yml`) are thin orchestration: they call actions in
order and wire their outputs together. This means:

- **Adding a framework** = teaching `detect-framework`, `install-dependencies`,
  `lint`, `test`, and `build` a new `case` branch each — not rewriting any
  workflow.
- **Adding an environment** = adding a block to `environments:` in
  `mobile-ci.yaml` — the workflows are already environment-agnostic.
- **Testing a single stage in isolation** is possible because each action
  has explicit inputs/outputs and no hidden global state beyond the
  checked-out repo.

## The reusable deploy workflow

`deploy-dev.yml`, `deploy-staging.yml`, and `deploy-prod.yml` are each ~15
lines: they call `_deploy-template.yml` (a `workflow_call` reusable
workflow) with a different `environment` and `play-track` input. The full
gate → build → sign → deploy → notify sequence is defined exactly once.

## Data flow

```
mobile-ci.yaml
    │
    ▼
validate-config  ──fails──▶ pipeline stops
    │
    ▼
monorepo-matrix.py  ──▶  { include: [ {name, path, framework}, ... ] }
    │
    ▼
per-app job (matrix) ──▶ detect-framework ──▶ setup-* ──▶ restore-cache
    ──▶ install-dependencies ──▶ lint ──▶ security ──▶ test ──▶ coverage
    ──▶ [gate] ──▶ feature-flags ──▶ versioning ──▶ build ──▶ signing
    ──▶ performance-regression [gate] ──▶ upload-artifact ──▶ deploy-play
    ──▶ cleanup ──▶ notify
```

Any gate step (`lint`, `security`, `test`, `coverage`,
`performance-regression`) exits non-zero on failure, which stops the job
before `deploy-play` ever runs — GitHub Actions does not continue past a
failed step unless it's explicitly marked `continue-on-error`, and none of
the gates are.
