# Kanban - workspace-core
Project scope: OpenClaw workspace automation, reliability, and agent tooling.

## Backlog

- [ ] **add test guardrails** (2026-03-03)
  - branch: `feature/workspace-core-add-test-guardrails-2026-03-03`
  - tests: define before coding
  - notes: ensure each task logs tests
- [ ] **Add config sanity checker for model/fallback paths**
  - branch: `feature/workspace-core-config-sanity-checker-2026-03-03`
  - tests: invalid provider IDs, duplicate fallback IDs, missing key checks
  - acceptance: command exits non-zero on invalid config
- [ ] **Implement stale-session pin detection and warning**
  - branch: `feature/workspace-core-session-pin-detection-2026-03-03`
  - tests: pinned model mismatch scenarios
  - acceptance: warning emitted with remediation instructions
- [ ] **Automate heartbeat task health summary**
  - branch: `feature/workspace-core-heartbeat-health-summary-2026-03-03`
  - tests: empty heartbeat, active heartbeat, error fallback
  - acceptance: summary log generated daily

## In Progress

## Review

## Done

- [x] **Create coding workflow guardrail script (branch + tests required)**
  - branch: `feature/workspace-core-coding-guardrails-2026-03-03`
  - tests: blocks direct main commits, blocks task closure without tests
  - acceptance: script usable by coding agent before marking task done
  - test-results: `bash tools/test_coding_workflow_guardrails.sh` => 10 passed
  - notes: Script created at tools/coding-workflow-guardrails.sh with full test suite
