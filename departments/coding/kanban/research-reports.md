# Kanban - research-reports

Project scope: publishable research assets, market scans, and monetizable reports.

## Backlog
- [ ] **Define report template with repeatable structure**
  - branch: `feature/research-reports-template-structure-2026-03-03`
  - tests: template completeness lint (required sections present)
  - acceptance: one reusable markdown template committed
- [ ] **Add citation/source checker script for report drafts**
  - branch: `feature/research-reports-source-checker-2026-03-03`
  - tests: missing link detection, duplicate source detection
  - acceptance: script reports broken/missing references
- [ ] **Create packaging pipeline for PDF + markdown exports**
  - branch: `feature/research-reports-export-pipeline-2026-03-03`
  - tests: export success and deterministic file names
  - acceptance: one command produces publish-ready bundle

## Ready

## In Progress

## Review
- [ ] **Build first monetizable report outline from existing income tracks**
  - branch: `feature/research-reports-first-offer-outline-2026-03-08-workspace`
  - tests: checklist validation against template
  - acceptance: outline ready for drafting and pricing
  - test-results: `python3 -m unittest tests/test_report_outline_validator.py -v` => 2 passed; `python3 tools/report_outline_validator.py research-reports/openclaw-income-tracks-first-offer-outline.md` => `REPORT_OUTLINE_VALID`
  - notes: added a reusable outline template, a validator CLI, and the first report outline anchored to the current workspace income-track strategy

## Done
