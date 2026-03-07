# Coding Department - Git Workflow Rules

## ⚠️ MANDATORY: Feature Branch Workflow (Effective Immediately)

All coding work MUST follow this workflow. No exceptions.

## Rules

1. **Never push directly to `main`**
   - `main` branch is protected
   - All work happens on feature branches
   - `main` only receives code via Pull Request merge

2. **Create feature branches for each task**
   ```bash
   git checkout -b feature/<task-name>-<YYYY-MM-DD>
   # Example: feature/contacts-map-room-schema-2026-03-04
   ```

3. **Push feature branches to GitHub**
   ```bash
   git push -u origin feature/<task-name>-<YYYY-MM-DD>
   ```

4. **Create Pull Request before merging**
   - Complete the task on the feature branch
   - Run tests and verify
   - Create PR: `feature/<task>` → `main`
   - Wait for review/approval (or self-approve if autonomous)
   - Merge PR to `main`

5. **Delete feature branches after merge**
   ```bash
   git branch -d feature/<task-name>-<YYYY-MM-DD>
   git push origin --delete feature/<task-name>-<YYYY-MM-DD>
   ```

## Branch Naming Convention

```
feature/<component>-<description>-<YYYY-MM-DD>
```

**Examples:**
- `feature/contacts-map-room-schema-2026-03-04`
- `feature/sync-import-pipeline-2026-03-05`
- `feature/graph-builder-dedup-2026-03-04`

## Workflow Summary

```bash
# 1. Start task
git checkout main
git pull
git checkout -b feature/my-task-2026-03-04

# 2. Work on task (commit frequently)
git add .
git commit -m "feat: implement my-task step 1"
git push -u origin feature/my-task-2026-03-04

# 3. Complete task
git commit -m "feat: complete my-task"
git push

# 4. Create PR via GitHub UI or CLI
# 5. Merge PR after review
# 6. Delete branch
```

## Enforcement

- Coding department runs will enforce this workflow
- Tasks without feature branches will be rejected
- Direct pushes to `main` will be blocked (repo settings)
- Each kanban card must reference its feature branch

## Questions?

See: `departments/coding/kanban/README.md` for kanban workflow
See: `AGENTS.md` for session context rules
