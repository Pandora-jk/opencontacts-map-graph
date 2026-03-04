# Android Shared Core Architecture

This document defines the initial shared-core module boundaries for the map ecosystem.

## Modules

- `:core-db`
  - Owns canonical geo storage contracts (`SharedGeoStore`, `GeoRecord`, `GeoBounds`).
  - Must not depend on Android UI or map rendering libraries.
- `:core-map`
  - Owns map tile cache contracts (`SharedTileCache`, `MapTileKey`, `MapTilePayload`).
  - Must not depend on contact or media domain entities.
- `:core-media`
  - Owns media metadata contracts (`SharedMediaIndex`, `MediaAsset`, `MediaGeoPoint`).
  - Must not depend on sync scheduling concerns.
- `:core-sync`
  - Owns background sync scheduling contracts (`SharedSyncScheduler`, `SyncTask`, `SyncDirection`).
  - Must remain transport-agnostic (no provider-specific SDK in core contract).

## Boundary Rules

- Cross-module communication happens through DTOs and interfaces only.
- `:app` can compose all modules; core modules should not depend on `:app`.
- Any Android platform details should be implemented in adapters above these contracts.

## Compatibility Contract Tests

Each core module has a JVM test suite validating:
- contract behavior (create/read/update/delete or schedule/cancel flows)
- DTO compatibility (stable field usage across module interfaces)

Test entry points:
- `:core-db:test` -> `CoreDbContractsTest`
- `:core-map:test` -> `CoreMapContractsTest`
- `:core-media:test` -> `CoreMediaContractsTest`
- `:core-sync:test` -> `CoreSyncContractsTest`
