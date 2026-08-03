# 📱 Enterprise Mobile CI/CD Platform

A modular, configuration-driven GitHub Actions platform for shipping **Flutter**, **React Native**, and **Native Android (Kotlin)** apps across **Development → Staging → Production** with strict quality, security, and approval gates.

---

## 📌 Table of Contents

- [Overview & Architecture](#-overview--architecture)
- [How Environments Work](#-how-environments-work)
- [Directory Layout](#-directory-layout)
- [Step-by-Step Setup Guide](#-step-by-step-setup-guide)
- [Environment Variables & Secrets Reference](#-environment-variables--secrets-reference)
- [Branching Strategy & Triggers](#-branching-strategy--triggers)
- [Local Config Validation](#-local-config-validation)
- [Emergency Rollbacks](#-emergency-rollbacks)
- [Documentation Reference](#-documentation-reference)

---

## 🏗️ Overview & Architecture

Instead of maintainers copying giant, repetitive GitHub Action workflow files into every application repository, this platform uses a **modular architecture**:

1. **Config-Driven Core (`mobile-ci.yaml`)**: Each application repository contains a single `mobile-ci.yaml` config at its root. Workflows read this configuration rather than hardcoding branch names, package IDs, or thresholds.
2. **JSON Schema Engine (`schemas/mobile-ci.schema.json`)**: Validates `mobile-ci.yaml` files before pipeline execution to prevent syntax or structural errors.
3. **Modular Composite Actions (`.github/actions/*`)**: Each pipeline step (framework detection, environment setup, linting, testing, security scanning, building, signing, deploying, notifying) is encapsulated in an isolated composite action.
4. **Thin Orchestration Workflows (`.github/workflows/*`)**: Workflows handle trigger logic, job dependency sequencing, environment secrets injection, and status reporting.

```
                  +-------------------------+
                  |     mobile-ci.yaml      |  (App Config)
                  +------------+------------+
                               |
                               v
                  +-------------------------+
                  | mobile-ci.schema.json   |  (Validation Engine)
                  +------------+------------+
                               |
                               v
      +------------------------+------------------------+
      |                        |                        |
      v                        v                        v
+-------------+        +---------------+        +--------------+
|  ci.yml     |        | deploy-dev.yml|        |deploy-prod.yml| (Workflows)
+------+------+        +-------+-------+        +-------+------+
       |                       |                        |
       +-----------------------+------------------------+
                               |
                               v
               +-------------------------------+
               | .github/actions/*             |
               | (detect, setup, lint, test,   | (Composite Actions)
               |  security, build, sign, play) |
               +-------------------------------+
```

---

## 🌍 How Environments Work

The platform manages 3 isolated environments out of the box:

```
[develop branch]  --->  Deploy Dev      --->  Google Play Internal Testing Track
[release/* branch] --->  Deploy Staging  --->  Google Play Beta Closed Testing Track
[main branch]     --->  Deploy Prod     --->  Google Play Production (10% Staged Rollout)
```

### 1. Development (`development`)
- **Trigger**: Pushes or pull requests merged into `develop`.
- **Target Track**: Google Play Store **Internal Testing Track**.
- **App ID**: `com.company.app.dev` (allows side-by-side installation with production apps).
- **Backend API**: Connected to development API servers.

### 2. Staging (`staging`)
- **Trigger**: Pushes to release candidate branches matching `release/*`.
- **Target Track**: Google Play Store **Closed Beta Track**.
- **App ID**: `com.company.app.staging`.
- **Backend API**: Connected to staging API servers for UAT and pre-release verification.

### 3. Production (`production`)
- **Trigger**: Code merged into `main`.
- **Target Track**: Google Play Store **Production Track**.
- **Protection**: Optional manual approval gate via GitHub Environment Reviewers.
- **Rollout Strategy**: **10% initial staged rollout**, which can be increased incrementally to 25%, 50%, and 100% after monitoring crash reports.

---

## 📂 Directory Layout

```
.github/
├── actions/                  # Reusable composite actions
│   ├── build/                # Compiles Flutter AAB/APK, RN bundle, or Gradle AAB
│   ├── deploy-play/          # Publishes signed AABs to Google Play tracks
│   ├── detect-framework/     # Auto-detects Flutter, RN, or Android Gradle
│   ├── lint/                 # Code analysis & formatting check
│   ├── notify/               # Slack & Email notification dispatcher
│   ├── security-scan/        # Gitleaks secret scan & dependency audit
│   ├── setup-env/            # JDK, Flutter SDK, Node.js & cache configuration
│   ├── signing/              # Base64 keystore decoding & signing
│   └── test/                 # Unit & integration test executor
└── workflows/                # Thin GitHub workflow orchestration
    ├── ci.yml                # PR validation gate
    ├── deploy-dev.yml        # Dev deploy on 'develop' push
    ├── deploy-staging.yml    # Staging deploy on 'release/*' push
    ├── deploy-prod.yml       # Production deploy on 'main' push
    └── rollback.yml          # Emergency rollback trigger

scripts/                      # DevOps helper scripts (versioning, changelog, perf budget)
schemas/                      # JSON Schema for mobile-ci.yaml
templates/                    # Starter mobile-ci.yaml template
examples/                     # Working config examples (Flutter, RN, Android, Monorepo)
docs/                         # Architecture, Security, Monitoring & Roadmap docs
.gitignore                    # Pre-configured Git ignore rules
.env.example                  # Secrets & Environment variables reference
```

---

## 🚀 Step-by-Step Setup Guide

To onboard a mobile app to this CI/CD platform:

### Step 1: Copy Platform Files to Your App Repo
Copy the core platform folders into your application repository:
```bash
cp -r .github scripts schemas templates/mobile-ci.yaml .env.example .gitignore /path/to/your-app-repo/
```

### Step 2: Configure `mobile-ci.yaml`
Edit `mobile-ci.yaml` in your app repository root to specify your package IDs, backend URLs, quality thresholds, and notification webhooks:
```yaml
version: 1
framework: auto

environments:
  development:
    branch: develop
    android:
      applicationId: com.yourcompany.app.dev
      backendUrl: https://dev-api.yourcompany.com
  staging:
    branch: "release/*"
    android:
      applicationId: com.yourcompany.app.staging
      backendUrl: https://staging-api.yourcompany.com
  production:
    branch: main
    android:
      applicationId: com.yourcompany.app
      backendUrl: https://api.yourcompany.com
```

### Step 3: Set Up GitHub Environments
In your GitHub Repository under **Settings → Environments**, create three environments:
1. `development`
2. `staging`
3. `production` *(Optional: Add Required Reviewers for manual approval gates)*

---

## 🔐 Environment Variables & Secrets Reference

Refer to [`.env.example`](.env.example) for the complete list of secrets needed in GitHub Actions.

### 🔑 Required Secrets (`Settings → Secrets and variables → Actions`)

| Secret Name | Description | How to Obtain / Generate |
|---|---|---|
| `ANDROID_KEYSTORE_BASE64` | Base64-encoded release `.keystore` / `.jks` file | `base64 -w 0 path/to/release.keystore` |
| `ANDROID_KEYSTORE_PASSWORD` | Password for the keystore | Keytool creation password |
| `ANDROID_KEY_ALIAS` | Alias name for the signing key | Keytool key alias |
| `ANDROID_KEY_PASSWORD` | Password for the key alias | Keytool key password |
| `PLAY_SERVICE_ACCOUNT_JSON` | Full JSON contents of Google Play Service Account key | Google Play Console → API Access → Service Accounts (Release Manager role) |
| `SLACK_WEBHOOK_URL` | *(Optional)* Slack Webhook URL | Slack API → Incoming Webhooks |

### 📌 Required Repository Variable (`Settings → Secrets and variables → Actions → Variables`)

| Variable Name | Description | Example Value |
|---|---|---|
| `ANDROID_APPLICATION_ID` | Package name of your Android application | `com.yourcompany.app` |

---

## 🌿 Branching Strategy & Triggers

- **Pull Requests (`PR -> develop, release/*, main`)**: Executes [`ci.yml`](.github/workflows/ci.yml) to run linting, unit tests, secret scanning, dependency checks, and a dry-run build.
- **Push to `develop`**: Executes [`deploy-dev.yml`](.github/workflows/deploy-dev.yml) to deploy to Google Play Internal Testing.
- **Push to `release/vX.Y.Z`**: Executes [`deploy-staging.yml`](.github/workflows/deploy-staging.yml) to deploy to Google Play Closed Beta.
- **Push to `main`**: Executes [`deploy-prod.yml`](.github/workflows/deploy-prod.yml) to trigger a 10% staged production rollout.

---

## 🧪 Local Config Validation

Before committing changes to `mobile-ci.yaml`, validate your configuration locally using Python:

```bash
python3 scripts/validate-config.py mobile-ci.yaml schemas/mobile-ci.schema.json
```

Output when valid:
```
mobile-ci.yaml is valid.
```

---

## ⏪ Emergency Rollbacks

If a bad production release occurs, trigger an emergency rollback without writing code:

1. Go to **GitHub Actions → Emergency Rollback Pipeline**.
2. Click **Run workflow**.
3. Select the `target_environment` (`production`, `staging`, or `development`).
4. Enter the `rollback_version_tag` (e.g., `v1.2.0`).
5. The pipeline rebuilds, signs, and re-promotes the specified release tag to the Google Play Store.

---

## 📚 Documentation Reference

- 📖 [Getting Started Guide](docs/GETTING_STARTED.md)
- ⚙️ [Configuration Reference](docs/CONFIGURATION.md)
- 🏛️ [Architecture Specifications](docs/ARCHITECTURE.md)
- 🔒 [Security & Threat Model](docs/SECURITY.md)
- 📊 [Monitoring & Telemetry](docs/MONITORING.md)
- 🗺️ [Roadmap & Extended Setup](docs/ROADMAP.md)

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
