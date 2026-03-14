# Android Ecosystem

This repository is the active Android monorepo for the first working Contacts app.

## Active Modules

- `:apps:contacts` - current Android application target
- `:core:database` - shared database contracts
- `:core:map` - shared map contracts
- `:core:media` - shared media contracts
- `:core:sync` - shared sync contracts

## Working Build

Prerequisites:

1. Set `ANDROID_SDK_ROOT` or create `local.properties` with `sdk.dir=...`
2. Use Java 17

Build the debug APK:

```bash
./gradlew :apps:contacts:assembleDebug
```

Build the signed release APK:

```bash
./gradlew :apps:contacts:assembleRelease
```

If your environment cannot write to `~/.gradle`, use a local Gradle cache:

```bash
GRADLE_USER_HOME=/tmp/gradle-android-ecosystem ./gradlew :apps:contacts:assembleDebug
```

APK output:

```text
apps/contacts/build/outputs/apk/debug/contacts-debug.apk
```

```text
apps/contacts/build/outputs/apk/release/contacts-release.apk
```

## CI and Releases

- `.github/workflows/contacts-android.yml` builds the debug APK on pushes and pull requests.
- Pushing a tag like `v1.0.0` builds a signed release APK and publishes it to GitHub Releases.
- Signed releases use `keystore.properties` locally and GitHub Actions secrets in CI.
- `docs/release-process.md` documents the required secrets and tag flow.

## Notes

- The live app code for the first working build is under `apps/contacts/src/main`.
- The legacy migrated prototype under `apps/contacts/main` is not part of the active build.
- `settings.gradle.kts` declares the monorepo module structure.
- Release signing is loaded from a local `keystore.properties` file at the repo root.
- Local Gradle execution is sandbox-limited here; GitHub Actions is the reliable APK verification path from this environment.
