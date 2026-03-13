# Kanban - automation-scripts
Project scope: PDF-to-CSV and related micro-automation tooling.

**STATUS:** This project is now on hold. Priority shifted to Android Contacts App.

## Backlog
- [ ] **Add CSV schema validator for generated outputs**
- [ ] **Add CLI flags for delimiter + encoding in `pdf_to_csv.py`**
- [ ] **Create smoke test command for sample PDF fixtures**

## Ready

- [ ] **Build complete UI layer for OpenContacts Map Graph Android app and ensure APK is built...** (2026-03-13)
  - branch: `feature/automation-scripts-build-complete-ui-layer-for-opencontacts-map-graph-android-app-and-ensure-apk-is-built-2026-03-13`
  - tests: define before coding
  - notes: Build complete UI layer for OpenContacts Map Graph Android app and ensure APK is built via GitHub Actions by tomorrow. Requirements: 1) Create MainActivity.kt with Compose setup, 2) Create ContactListScreen composable, 3) Create ContactViewModel, 4) Add theme files (Theme.kt, Color.kt, Type.kt), 5) Add resource files (strings.xml, colors.xml, themes.xml) if missing, 6) Commit and push to main branch to trigger CI/CD, 7) Verify GitHub Actions builds APK successfully, 8) Create GitHub release with APK artifact. Priority: HIGH - deadline is tomorrow.
## In Progress
## Review
## Done
- [x] **Write unit tests for `pdf_to_csv.py` core conversion path**
  - ✅ **COMPLETED AND MERGED** - 2026-03-12
  - Tests: 8/8 passing
  - Coverage: 73% (core conversion path well tested)
  - Branch: merged to main
  - Notes: Task completed successfully. Remaining 27% is error handling paths (import failure, exception handling) which can be addressed in future iterations if needed.
