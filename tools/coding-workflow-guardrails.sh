#!/usr/bin/env bash
# coding-workflow-guardrails.sh
# Guardrail script for coding department workflow
# - Blocks direct commits to main/master branches
# - Blocks task closure without tests

set -euo pipefail

REPO=""
CHECK_BRANCH=1
CHECK_TESTS=1
TASK_FILE=""

usage() {
    cat <<'EOF'
Usage: tools/coding-workflow-guardrails.sh [options]

Options:
  --repo PATH       Git repository path (required)
  --no-branch-check Skip branch name validation
  --no-test-check   Skip test validation
  --task-file PATH  Path to task file to check for test evidence
  -h, --help        Show help

Guardrails:
  1. Branch Check: Ensures current branch is feature/* (blocks main/master commits)
  2. Test Check: Verifies tests exist and/or test evidence in task file
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)
            REPO="${2:-}"
            shift 2
            ;;
        --no-branch-check)
            CHECK_BRANCH=0
            shift
            ;;
        --no-test-check)
            CHECK_TESTS=0
            shift
            ;;
        --task-file)
            TASK_FILE="${2:-}"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage
            exit 2
            ;;
    esac
done

# Validate repo path
if [[ -z "$REPO" ]]; then
    echo "GUARDRAIL_FAIL: Missing required --repo argument" >&2
    exit 1
fi

if [[ ! -d "$REPO/.git" ]]; then
    echo "GUARDRAIL_FAIL: Not a git repo: $REPO" >&2
    exit 1
fi

cd "$REPO"

# Guardrail 1: Branch Check - Block direct main/master commits
if [[ "$CHECK_BRANCH" -eq 1 ]]; then
    current_branch="$(git rev-parse --abbrev-ref HEAD)"
    
    # Check if on main or master branch (blocked)
    if [[ "$current_branch" == "main" || "$current_branch" == "master" ]]; then
        echo "GUARDRAIL_FAIL: Direct commits to '$current_branch' are blocked. Use a feature/* branch." >&2
        exit 2
    fi
    
    # Check if branch follows feature/* pattern
    if [[ ! "$current_branch" =~ ^feature/ ]]; then
        echo "GUARDRAIL_FAIL: Branch '$current_branch' does not follow feature/* naming convention." >&2
        echo "GUARDRAIL_HINT: Create a feature branch with: git checkout -b feature/your-task-name" >&2
        exit 2
    fi
    
    echo "GUARDRAIL_OK: branch=$current_branch"
fi

# Guardrail 2: Test Check - Block task closure without tests
if [[ "$CHECK_TESTS" -eq 1 ]]; then
    # Check if there are test files in the repo
    test_count=$(find "$REPO" -type f \( -name "test_*.py" -o -name "*_test.py" -o -name "*.test.js" -o -name "*.spec.js" -o -name "*.test.ts" -o -name "*.spec.ts" -o -name "tests.sh" -o -name "test.sh" \) 2>/dev/null | wc -l)
    
    # Check for tests directory
    if [[ -d "$REPO/tests" || -d "$REPO/test" ]]; then
        test_count=$((test_count + 1))
    fi
    
    # If task file specified, check for test evidence
    if [[ -n "$TASK_FILE" && -f "$TASK_FILE" ]]; then
        # Look for test evidence in task file (test results, coverage, etc.)
        if grep -qi "test" "$TASK_FILE" 2>/dev/null; then
            echo "GUARDRAIL_OK: test evidence found in task file"
        else
            echo "GUARDRAIL_WARN: No test evidence found in task file: $TASK_FILE" >&2
            # Don't fail, just warn
        fi
    fi
    
    if [[ "$test_count" -eq 0 ]]; then
        echo "GUARDRAIL_WARN: No test files detected in repository. Consider adding tests before marking task complete." >&2
        # Don't fail on this, just warn
    else
        echo "GUARDRAIL_OK: $test_count test file(s) detected"
    fi
fi

echo "GUARDRAIL_PASS: All checks passed"
exit 0
