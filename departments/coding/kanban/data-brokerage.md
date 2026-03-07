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

- [ ] **Android shared core: implement shared Room schema + migration strategy**
  - branch: `feature/data-brokerage-android-shared-room-schema-migrations-2026-03-04`
  - tests: Room migration tests (forward/backward compatibility), referential integrity checks
  - acceptance: one shared DB layer supports contacts and photo metadata entities without duplicate storage

- [ ] **Android shared core: build shared map tile/cache manager**
  - branch: `feature/data-brokerage-android-shared-map-cache-manager-2026-03-04`
  - tests: cache hit/miss behavior, eviction policy tests, offline map retrieval tests
  - acceptance: contacts and gallery screens use same cache and avoid duplicate tile downloads

- [ ] **Android shared core: implement unified background sync scheduler**
  - branch: `feature/data-brokerage-android-shared-sync-scheduler-2026-03-04`
  - tests: WorkManager scheduling tests, retry/backoff tests, battery/network constraint tests
  - acceptance: one scheduler coordinates sync for both apps and prevents duplicate jobs

- [ ] **Android app for geo-gallery using the same shared map core** (Epic, 2026-03-04)
  - branch: `feature/data-brokerage-android-geo-gallery-epic-2026-03-04`
  - tests: epic checklist only
  - acceptance: gallery app displays photos on same map foundation and links with contacts context
  - notes: app should support shared map view mode to switch between contacts and photos quickly

- [ ] **Android geo-gallery: import photos + extract geotags into shared metadata store**
  - branch: `feature/data-brokerage-android-geo-gallery-import-geotags-2026-03-04`
  - tests: unit (EXIF parse success/failure), integration (import batch with mixed geotags)
  - acceptance: photo metadata ingested into shared DB; missing geotags handled deterministically

- [ ] **Android geo-gallery: map photo clusters + timeline drill-down**
  - branch: `feature/data-brokerage-android-geo-gallery-clusters-timeline-2026-03-04`
  - tests: instrumentation (cluster render, zoom transitions, timeline filter behavior)
  - acceptance: photos render as clusters on map and can be filtered by date range

- [ ] **Android ecosystem: cross-app deep links (contact <-> location <-> photo)**
  - branch: `feature/data-brokerage-android-ecosystem-cross-app-deeplinks-2026-03-04`
  - tests: integration (deep link contracts), instrumentation (open contact then related photos)
  - acceptance: users can jump between contacts and gallery context without losing selected map state

- [ ] **Android ecosystem: shared resource budget + perf benchmark suite**
  - branch: `feature/data-brokerage-android-ecosystem-shared-perf-benchmarks-2026-03-04`
  - tests: macrobenchmark (startup/memory/scroll), storage usage regression tests per build
  - acceptance: baseline metrics tracked; shared-core approach proves lower storage and better runtime behavior

- [ ] **Android app for syncing mappoints between map tools** (Epic, 2026-03-04)
  - branch: `feature/data-brokerage-android-sync-epic-2026-03-04`
  - tests: epic checklist only
  - acceptance: all sync subtasks below shipped and verified
  - notes: MVP local-first sync engine between map tools; pluggable adapter layer for future providers

- [ ] **Android sync: implement import pipeline + conflict resolution**
  - branch: `feature/data-brokerage-android-sync-import-conflicts-2026-03-04`
  - tests: integration (import->normalize->dedup), conflict tests (same id newer timestamp wins)
  - acceptance: imports merge correctly; conflict policy deterministic and logged

- [ ] **Android sync: implement export pipeline + round-trip validator**
  - branch: `feature/data-brokerage-android-sync-export-roundtrip-2026-03-04`
  - tests: integration (canonical->GeoJSON/KML->canonical), round-trip field preservation
  - acceptance: round-trip does not lose id/name/lat/lon/tags; output files load in target tools

- [ ] **Android sync: sync report + local activity log UI**
  - branch: `feature/data-brokerage-android-sync-report-ui-2026-03-04`
  - tests: instrumentation (run sync and validate added/updated/skipped report rendering)
  - acceptance: report screen and local log show per-run results with timestamps

- [ ] **Android app for showing contacts on a map with connection graph** (Epic, 2026-03-04)
  - branch: `feature/data-brokerage-android-contacts-map-graph-epic-2026-03-04`
  - tests: epic checklist only
  - acceptance: all map/graph subtasks below shipped and verified
  - notes: MVP with Room DB + MapLibre + graph panel; relationship rules configurable via local JSON

- [ ] **Android contacts-map: scaffold app module + Room schema**
  - branch: `feature/data-brokerage-android-contacts-map-room-schema-2026-03-04`
  - tests: unit (Room migrations), instrumentation (db CRUD for contact + relationship entities)
  - acceptance: app boots; Room schema stores contacts and edges reliably

- [ ] **Android contacts-map: map markers + search/filter**
  - branch: `feature/data-brokerage-android-contacts-map-markers-filter-2026-03-04`
  - tests: instrumentation (marker render, search query, tag/group filter)
  - acceptance: contacts render on map; filter/search updates marker set correctly

- [ ] **Android contacts-map: graph builder + edge dedup rules**
  - branch: `feature/data-brokerage-android-contacts-graph-builder-2026-03-04`
  - tests: unit (graph construction, shared-org/tag rules, edge dedup)
  - acceptance: deterministic graph output from same contact dataset

- [ ] **Android contacts-map: graph panel + deep-link contact->map->graph**
  - branch: `feature/data-brokerage-android-contacts-graph-panel-deeplink-2026-03-04`
  - tests: integration (tap contact opens map and graph detail), instrumentation nav tests
  - acceptance: deep-link flow works end-to-end and preserves selected contact context

- [ ] **Android contacts-map: offline snapshot cache + performance pass**
  - branch: `feature/data-brokerage-android-contacts-offline-perf-2026-03-04`
  - tests: instrumentation (cold start with offline snapshot), performance (1k contacts target frame budget)
  - acceptance: offline snapshot loads reliably and UI remains responsive at target dataset size
- [ ] **Expand solar sample workflow toward 500-entry production list**
  - branch: `feature/data-brokerage-solar-500-workflow-2026-03-03`
  - tests: row count, schema validation, no duplicate primary contacts
  - acceptance: export pipeline reproducibly generates target list

## In Progress
- [ ] **Android map ecosystem: shared core SDK (storage/map/sync primitives)** (Epic, 2026-03-04)
  - branch: `feature/data-brokerage-android-map-ecosystem-shared-core-epic-sprint2-2026-03-06`
  - tests: `gradle8 :core-sdk:test` (blocked by sandbox native library error), `python3 -m unittest discover -s tests -v` (6 passed, 2 failed pre-existing), `python3 -m unittest tests.test_pdf_to_csv.PdfToCsvTests -v` (5 passed)
  - acceptance: contacts app and gallery app both consume common modules without data duplication
  - notes: created `core-sdk` gateway module, wired `core-db/core-map/core-media/core-sync` in Gradle settings, and added cross-gateway sharing tests for storage/tile/media primitives.

## Review
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
