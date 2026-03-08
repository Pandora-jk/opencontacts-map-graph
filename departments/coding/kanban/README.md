# Coding Kanban Boards

Boards:
- `automation-scripts.md`
- `data-brokerage.md`
- `research-reports.md`
- `workspace-core.md`

Workflow:
1. Break tasks into cards in `Backlog`.
2. Move selected cards to `Ready` with acceptance criteria + tests.
3. Start work only from `Ready` on a feature branch.
4. Move to `Review` with test results.
5. Let the feedback loop audit every unmerged feature branch and assign it to `coding_agent` or `review_agent`.
6. Merge only when the branch is in `Review`, has recorded test evidence, is pushed to `origin`, and passes the merge gate against `main`.
7. Move to `Done` only after merge/delete verification.
