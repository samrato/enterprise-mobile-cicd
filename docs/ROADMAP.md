# Roadmap / Extended Features

Everything below has a real, working action wired into the platform — but
each depends on something you set up outside this repo (a third-party
account, a Fastlane project, a Storybook build). Nothing here is
hand-wavy config; each flag genuinely turns the corresponding action on
and it will run, or fail loudly explaining what's missing.

### iOS App Store deployment
Action: `.github/actions/deploy-appstore`. Prerequisites:
1. `fastlane init` in your repo with a lane the action can call (default: `beta`).
2. An App Store Connect API key, base64-encoded, in secret `APP_STORE_CONNECT_API_KEY`.
3. Set `ios.enabled: true` and fill `ios.scheme` / `ios.appstore.groups` in `mobile-ci.yaml`.
4. Add an iOS build step to a new `build-ios` variant of the `build`
   action (this platform ships the Android build path fully; the iOS
   `.ipa` build step is the one piece you'll add for your specific Xcode
   project setup, since signing certificates/provisioning profiles vary
   per org).

### Multi-app monorepo
Fully implemented. Set `monorepo.enabled: true` and list `apps:` in
`mobile-ci.yaml` — `scripts/monorepo-matrix.py` fans every workflow out
into one job per app automatically.

### Automatic changelog generation
Fully implemented. `.github/actions/changelog` + `scripts/generate-changelog.sh`
parse conventional commits since the last tag; `release.yml` commits the
result and attaches it to the GitHub Release.

### Automatic dependency updates
Config files (`renovate.json`, `.github/dependabot.yml`) are included and
functional as-is — enable the Renovate GitHub App on your repo, or
Dependabot under *Settings → Code security*, matching whichever
`dependencies.provider` you set.

### Performance regression testing
Action: `.github/actions/performance-regression`. Ships working for
`metric: apk_size` (compares signed artifact size against a cached
baseline). `metric: startup_time` requires you to populate a
`startup-time.txt` file earlier in the job from your own instrumented
test — the action reads it, it doesn't produce it.

### Visual UI regression testing
Action: `.github/actions/visual-regression`. Requires a Chromatic or Percy
account, a `CHROMATIC_PROJECT_TOKEN`/`PERCY_TOKEN` secret, and (for
Chromatic) a Storybook build in the repo. Fails loudly if the token is
missing rather than silently skipping.

### Feature flag integration
Action: `.github/actions/feature-flags`. Supports Firebase Remote Config
(via a GCP service account) and LaunchDarkly (via SDK key) out of the box;
`provider: none` is a no-op. Extend the `build` action to pass the
generated JSON into your app (`--dart-define-from-file` for Flutter is the
one-line addition).
