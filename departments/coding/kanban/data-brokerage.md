# Kanban - data-brokerage

Project scope: lead generation pipeline, data quality, and packaging for sale.

## Long-Term Goals (App Ecosystem)
- Build a shared Android ecosystem where multiple apps reuse one local data/storage core.
- Ship two user-facing apps on the same map foundation:
  - Contacts app: contact intelligence map + connection graph.
  - Gallery app: geo-linked photo browsing and timeline.
- Reuse resources across apps to reduce storage and improve performance:
  - shared Room database schema
  - shared map tile/cache layer
  - shared media/index metadata service
  - shared sync/import-export engine
- Keep modules replaceable: each app can evolve independently while keeping shared core backward-compatible.

## Backlog
- [ ] **Android map ecosystem: shared core SDK (storage/map/sync primitives)** (Epic, 2026-03-04) [SANDBLOCKED]
- branch: `feature/data-brokerage-android-map-ecosystem-shared-core-epic-sprint2-2026-03-06`
- tests: `gradle8 :core-sdk:test` (blocked by sandbox native library error)
- acceptance: contacts app and gallery app both consume common modules without data duplication
- notes: Requires non-sandbox environment with Android SDK. Created `core-sdk` gateway module.

- [ ] **Add lead de-duplication utility with deterministic matching**
  - branch: `feature/data-brokerage-lead-dedup-utility-2026-03-03`
  - tests: duplicate email/phone/address normalization cases
  - acceptance: duplicate rate reduced and logged per batch
- [ ] **Build data quality report generator (`quality_report.md`)**
  - branch: `feature/data-brokerage-quality-report-generator-2026-03-03`
  - tests: missing fields %, invalid contact format %, niche distribution
  - acceptance: report generated for each dataset release
- [ ] **Add license + usage terms template per sold dataset**
  - branch: `feature/data-brokerage-license-template-2026-03-03`
  - tests: template fields populated from metadata
  - acceptance: package includes clear buyer usage terms

## Ready
- [ ] **Expand solar sample workflow toward 500-entry production list**
- [ ] **Android app for geo-gallery using the same shared map core** (Epic, 2026-03-04)
- [ ] **Android geo-gallery: import photos + extract geotags into shared metadata store**
- [ ] **Android geo-gallery: map photo clusters + timeline drill-down**
- [ ] **Android ecosystem: cross-app deep links (contact <-> location <-> photo)**
- [ ] **Android ecosystem: shared resource budget + perf benchmark suite**
- [ ] **Android app for syncing mappoints between map tools** (Epic, 2026-03-04)
- [ ] **Android sync: implement import pipeline + conflict resolution**
- [ ] **Android sync: implement export pipeline + round-trip validator**
- [ ] **Android sync: sync report + local activity log UI**
- [ ] **Android app for showing contacts on a map with connection graph** (Epic, 2026-03-04)
- [ ] **Android contacts-map: scaffold app module + Room schema**
- [ ] **Android contacts-map: map markers + search/filter**
- [ ] **Android contacts-map: graph builder + edge dedup rules**
- [ ] **Android contacts-map: graph panel + deep-link contact->map->graph**
- [ ] **Android contacts-map: offline snapshot cache + performance pass**
## In Progress
- [ ] **Expand solar sample workflow toward 500-entry production list**
- branch: `feature/data-brokerage-solar-500-workflow-2026-03-03`
- tests: row count, schema validation, no duplicate primary contacts
- acceptance: export pipeline reproducibly generates target list

## Review
- [ ] **Android shared core: implement unified background sync scheduler**
  - branch: `feature/data-brokerage-android-shared-sync-scheduler-2026-03-04`
  - tests: `bash opencontacts-map-graph/scripts/run-shared-core-contract-tests.sh` => `CoreDbContractsTest` 4 passed, `CoreMapContractsTest` 7 passed, `CoreMediaContractsTest` 4 passed, `CoreSyncContractsTest` 6 passed
  - acceptance: one scheduler coordinates sync for both apps and prevents duplicate jobs
  - notes: expanded `core-sync` with shared dedupe keys, runtime constraints, duplicate-claim protection, and retry/backoff semantics so future WorkManager adapters for contacts/gallery can share one scheduling contract

- [ ] **Android shared core: build shared map tile/cache manager**
  - branch: `feature/data-brokerage-android-shared-map-cache-manager-2026-03-04`
  - tests: cache hit/miss behavior, eviction policy tests, offline map retrieval tests
  - acceptance: contacts and gallery screens use same cache and avoid duplicate tile downloads
  - test-results: `bash opencontacts-map-graph/scripts/run-shared-core-contract-tests.sh` => `CoreDbContractsTest` 4 passed, `CoreMapContractsTest` 7 passed, `CoreMediaContractsTest` 4 passed, `CoreSyncContractsTest` 4 passed; `/opt/gradle/gradle-8.7/bin/gradle :core-map:test` blocked in sandbox (`Could not determine a usable wildcard IP for this machine`)
  - notes: added `SharedTileCacheManager` with shared `load(...)`, offline-only reads, LRU eviction, and cache stats; `SharedCoreRegistry` now composes one shared manager instance so contacts/gallery flows can reuse the same tile cache contract

- [ ] **Android shared core: implement shared Room schema + migration strategy**
  - branch: `feature/data-brokerage-android-shared-room-schema-migrations-2026-03-04`
  - tests: Room migration tests (forward/backward compatibility), referential integrity checks
  - acceptance: one shared DB layer supports contacts and photo metadata entities without duplicate storage
  - test-results: direct Kotlin/JUnit run via `K2JVMCompiler` + `JUnitCore` => `CoreDbContractsTest` 7 passed
  - notes: added `SharedDbSchemas` (`v1` legacy `geo_records`, `v2` normalized `shared_locations/shared_contacts/shared_media`), `SharedDbIntegrity.validate(...)`, and factory-based `SharedGeoStores.inMemory()` for the shared DB contract surface

- [ ] **Android shared core: define modular architecture + API contracts**
  - branch: `feature/data-brokerage-android-shared-core-architecture-contracts-2026-03-04`
  - tests: contract tests for module boundaries and DTO compatibility
  - acceptance: architecture doc + enforced interface layer for `core-db`, `core-map`, `core-media`, `core-sync`
  - test-results: `bash opencontacts-map-graph/scripts/run-shared-core-contract-tests.sh` => `CoreDbContractsTest` 4 passed, `CoreMapContractsTest` 4 passed, `CoreMediaContractsTest` 4 passed, `CoreSyncContractsTest` 4 passed
  - notes: enabled explicit API mode across `core-db/core-map/core-media/core-sync`, hid in-memory implementations behind interface-returning factories, expanded `opencontacts-map-graph/docs/android-shared-core-architecture.md`, and rewired `SharedCoreRegistry` to compose only the public contract layer

- [ ] **Android sync: define canonical point schema + adapters (GeoJSON/KML)**
  - branch: `feature/data-brokerage-android-sync-schema-adapters-2026-03-04`
  - tests: unit (schema validation, adapter parse success/fail cases)
  - acceptance: canonical model finalized; GeoJSON/KML adapters parse to canonical objects
  - test-results: blocked in sandbox (`gradle8` fails with native/socket restrictions); fallback suite run: `python3 -m unittest tests/test_pdf_to_csv.py -v` => 6 passed, 2 failed (`ModuleNotFoundError: pdf_to_csv_under_test`, pre-existing)
  - notes: implemented `core-sync` module with canonical point model + GeoJSON/KML adapters and unit tests; awaiting runnable Android/Kotlin test environment for verification

## Done
