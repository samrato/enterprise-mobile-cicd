# Security Model

- **Secrets** live only in GitHub Secrets, never in `mobile-ci.yaml` or the
  repo. `mobile-ci.yaml` references secrets by *name*
  (`notifications.slack.webhookSecret: SLACK_WEBHOOK_URL`), never by value.
- **Keystore handling**: `ANDROID_KEYSTORE_BASE64` is decoded to a file
  under `$RUNNER_TEMP` (the runner's ephemeral, per-job tmpfs) by
  `scripts/decode-keystore.sh`, used only by the `signing` action, and
  shredded by `scripts/cleanup-secrets.sh` in an `if: always()` step — so
  it's removed even if signing fails.
- **Service-account JSON** (Play, Firebase, App Store Connect) is written
  to `$RUNNER_TEMP` immediately before use and shredded immediately after,
  the same pattern.
- **Least privilege**: the Play Console service account should be granted
  only the "Release manager" role for the specific app(s) it deploys, not
  Admin. The Firebase service account (for feature flags) should be scoped
  to Remote Config read access only.
- **Dependency scanning** runs per-framework (`npm audit`, Dart's `pana`,
  or the OWASP Dependency-Check Gradle plugin) and is a hard gate when
  `security.dependency_scan: true`.
- **Secret scanning** runs via `gitleaks` on every CI and deploy run.
- **Artifact integrity**: when `security.artifact_checksum: true`, upload a
  SHA-256 of the signed artifact alongside it in `deploy-play` / the
  release assets, so downstream consumers can verify it wasn't tampered
  with in transit. (Wire this into the `build` action's output if you need
  it — the config flag is read by convention; extend `build/action.yml`'s
  final step to `sha256sum` the artifact next to it.)
- **Signed releases**: every artifact that reaches a Play track has passed
  `apksigner verify` (APK) or `jarsigner` (AAB) in the `signing` action —
  an unsigned or corrupt-signature artifact never reaches `deploy-play`.
