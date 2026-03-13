# Kanban - automation-scripts
Project scope: PDF-to-CSV and related micro-automation tooling.

**STATUS:** This project is now on hold. Priority shifted to Android Contacts App.

## Backlog
- [ ] **Add CSV schema validator for generated outputs**
- [ ] **Add CLI flags for delimiter + encoding in `pdf_to_csv.py`**
- [ ] **Create smoke test command for sample PDF fixtures**

## Ready

## In Progress
- [ ] **Build complete UI layer for OpenContacts Map Graph Android app and ensure APK is built...** (2026-03-13)
  - branch: `feature/automation-scripts-build-complete-ui-layer-for-opencontacts-map-graph-android-app-and-ensure-apk-is-built-2026-03-13`
  - commits:
    - `def21e7` `feat: Add contact list UI with Material 3`
    - `df4a583` `fix(app): unblock contact data compilation`
    - `f4c3f8e` `feat(app): refine compose contact dashboard`
  - tests:
    - `java -cp '/opt/gradle/gradle-8.7/lib/*' org.jetbrains.kotlin.cli.jvm.K2JVMCompiler ... ContactFormatting.kt ContactRepositoryTest.kt`
    - `java -cp '/tmp/opencontacts-kotlin-tests-3:...' org.junit.runner.JUnitCore com.opencontacts.mapgraph.data.repository.ContactRepositoryTest`
    - result: `OK (3 tests)`
  - implementation:
    - fixed pre-existing `ContactDao`/`ContactRepository` Kotlin syntax blockers and extracted pure formatting helpers
    - upgraded `MainActivity`, `ContactListScreen`, and `ContactViewModel` with permission retry flow, dashboard summary, search, and safer loading/geocoding state handling
    - added `Type.kt` plus refreshed theme/resource files so the Compose UI layer is complete and consistent
    - removed missing app icon resource references that would block manifest compilation in CI
  - blockers:
    - `git push -u origin feature/automation-scripts-build-complete-ui-layer-for-opencontacts-map-graph-android-app-and-ensure-apk-is-built-2026-03-13` failed in sandbox: `Could not resolve host: github.com`
    - local Android Gradle tasks remain sandbox-blocked (`Could not determine a usable wildcard IP for this machine`), so GitHub Actions APK/release verification is still pending the remote push
## Review
## Done
- [x] **Write unit tests for `pdf_to_csv.py` core conversion path**
  - ✅ **COMPLETED AND MERGED** - 2026-03-12
  - Tests: 8/8 passing
  - Coverage: 73% (core conversion path well tested)
  - Branch: merged to main
  - Notes: Task completed successfully. Remaining 27% is error handling paths (import failure, exception handling) which can be addressed in future iterations if needed.
