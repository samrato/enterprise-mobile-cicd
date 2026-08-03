# Getting Started

## 1. Copy the platform into your repo
Copy `.github/`, `scripts/`, `schemas/`, and `templates/mobile-ci.yaml` (as
`mobile-ci.yaml`, at your repo root) into your mobile app repository.

## 2. Fill in mobile-ci.yaml
Start from `templates/mobile-ci.yaml`, or one of `examples/*/mobile-ci.yaml`
that matches your framework. Set `framework:` to `auto` unless you have a
reason to pin it, and fill in each environment's `applicationId` /
`backendUrl` / `firebaseProject`.

## 3. Add repository secrets
See `.env.example` for the full list. At minimum you need:
- `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`
- `PLAY_SERVICE_ACCOUNT_JSON`

Add a repository **variable** (not secret) `ANDROID_APPLICATION_ID`.

## 4. Set up GitHub Environments
Create `development`, `staging`, and `production` environments under
*Settings → Environments*. Add a required reviewer to `production` if you
want a manual approval gate before every prod deploy — GitHub will pause
the `deploy` job until approved.

## 5. Push
- Push to `develop` → `deploy-dev.yml` runs, deploys to the Play Internal track.
- Push to `release/x.x.x` → `deploy-staging.yml` runs, deploys to Closed Testing.
- Merge to `main` → `deploy-prod.yml` runs a staged production rollout.

## 6. (Optional) Enable extended features
Each of these needs its own external setup before flipping the switch in
`mobile-ci.yaml` — see `docs/ROADMAP.md` for what each one requires:
- iOS App Store deployment (`ios.enabled: true`)
- Visual regression testing (`testing.visual_regression.enabled: true`)
- Performance regression testing (`testing.performance_regression.enabled: true`)
- Feature flags (`environments.*.featureFlags.provider`)
- Monorepo builds (`monorepo.enabled: true`)
