# Android Shared Core Architecture

This document defines the shared-core API layer for the map ecosystem and the rules that keep contacts, gallery, and sync features decoupled.

## Module Contracts

- `:core-db`
  - Public API: `GeoRecord`, `GeoBounds`, `SharedGeoStore`, `SharedGeoStores.inMemory()`
  - Responsibility: canonical geo storage DTOs and repository contract
  - Forbidden dependencies: Android APIs, `:app`, `:core-map`, `:core-media`, `:core-sync`
- `:core-map`
  - Public API: `MapTileKey`, `MapTilePayload`, `SharedTileCache`, `SharedTileCaches.inMemory()`
  - Responsibility: map tile caching contract only
  - Forbidden dependencies: Android APIs, `:app`, `:core-db`, `:core-media`, `:core-sync`
- `:core-media`
  - Public API: `MediaGeoPoint`, `MediaAsset`, `SharedMediaIndex`, `SharedMediaIndexes.inMemory()`
  - Responsibility: media metadata indexing contract only
  - Forbidden dependencies: Android APIs, `:app`, `:core-db`, `:core-map`, `:core-sync`
- `:core-sync`
  - Public API: `SyncDirection`, `SyncTask`, `SharedSyncScheduler`, `SharedSyncSchedulers.inMemory()`
  - Responsibility: background sync scheduling contract only
  - Forbidden dependencies: Android APIs, `:app`, `:core-db`, `:core-map`, `:core-media`

## Enforcement Rules

- Core modules use Kotlin explicit API mode so every public contract is intentional.
- In-memory implementations are `internal`; callers compose modules through factory objects that return interfaces.
- Core module Gradle files must not declare `project(...)` dependencies on sibling modules.
- Android and provider-specific adapters belong above the contract layer and are composed by `:app`.

## DTO Stability Contract

- Constructor parameter names and JVM types are treated as the compatibility surface for DTOs.
- Any change to a public DTO requires updating its contract test and this document in the same branch.
- Nullable fields are preserved in the compatibility checks to avoid silent schema drift between apps.

## Composition Path

- `:app` depends on all four core modules and builds a `SharedCoreRegistry`.
- `SharedCoreRegistry` receives only interfaces from `SharedGeoStores`, `SharedTileCaches`, `SharedMediaIndexes`, and `SharedSyncSchedulers`.
- Future Room, disk-cache, media-index, and WorkManager adapters replace the internal in-memory implementations without changing the API surface.

## Contract Test Coverage

Each module test suite validates:

- behavior of the public contract
- factory methods returning interface types
- DTO constructor compatibility signatures
- module boundary rules in source imports and Gradle dependencies

Entry points:

- `:core-db:test` -> `CoreDbContractsTest`
- `:core-map:test` -> `CoreMapContractsTest`
- `:core-media:test` -> `CoreMediaContractsTest`
- `:core-sync:test` -> `CoreSyncContractsTest`

Sandbox-friendly local runner:

- `bash scripts/run-shared-core-contract-tests.sh`
