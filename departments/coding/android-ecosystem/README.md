# Android Map Ecosystem

This repository defines a multi-module Android project for a shared map ecosystem SDK with two independent app surfaces.

## Modules

- `core-sdk`: Android library module that holds reusable domain logic, shared services, and platform integrations for the ecosystem.
- `contacts-app`: Android application module for contacts-oriented map experiences. Depends on `core-sdk`.
- `gallery-app`: Android application module for gallery-oriented map experiences. Depends on `core-sdk`.

## Architecture

The project uses a hub-and-spoke module layout:

- `core-sdk` is the shared dependency hub.
- `contacts-app` and `gallery-app` are leaf application modules.
- Shared code should move into `core-sdk` when it is reused by more than one app or represents common platform capabilities.
- App-specific UI, navigation, and feature wiring should stay inside each application module.

## Build Structure

- `settings.gradle.kts` declares the three modules and central repository management.
- The root `build.gradle.kts` pins Android Gradle Plugin versions and exposes a standard `clean` task.
- Each module owns its own Android plugin configuration and namespace.

## Suggested Next Steps

1. Add `local.properties` or set `ANDROID_SDK_ROOT` so Gradle can locate the Android SDK.
2. Add source sets under each module, such as `src/main/java` or `src/main/kotlin`.
3. Move shared networking, storage, and map integration code into `core-sdk`.
4. Add tests for `core-sdk` before expanding app-specific features.
