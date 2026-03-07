#!/usr/bin/env bash
# Test suite for coding-workflow-guardrails.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GUARDRAIL_SCRIPT="$SCRIPT_DIR/coding-workflow-guardrails.sh"
TEST_REPO=""
TESTS_PASSED=0
TESTS_FAILED=0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_test() {
    echo -e "${GREEN}PASS${NC}: $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail_test() {
    echo -e "${RED}FAIL${NC}: $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

warn_test() {
    echo -e "${YELLOW}WARN${NC}: $1"
}

# Setup: Create a temporary test repository
setup_test_repo() {
    TEST_REPO="$(mktemp -d)/test-repo"
    mkdir -p "$TEST_REPO"
    cd "$TEST_REPO"
    git init -q
    git config user.email "test@example.com"
    git config user.name "Test User"
    echo "# Test Repo" > README.md
    git add README.md
    git commit -q -m "Initial commit"
    git remote add origin https://github.com/test/test-repo.git
}

# Cleanup: Remove test repository
cleanup_test_repo() {
    if [[ -n "$TEST_REPO" && -d "$TEST_REPO" ]]; then
        rm -rf "$TEST_REPO"
    fi
}

# Test: Script exists and is executable
test_script_exists() {
    if [[ -x "$GUARDRAIL_SCRIPT" ]]; then
        pass_test "Script exists and is executable"
    else
        fail_test "Script does not exist or is not executable: $GUARDRAIL_SCRIPT"
    fi
}

# Test: Missing repo argument should fail
test_missing_repo_arg() {
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" 2>&1); then
        fail_test "Should fail when --repo is missing"
    else
        if [[ "$output" == *"Missing required --repo"* ]]; then
            pass_test "Fails correctly with missing --repo argument"
        else
            fail_test "Error message should mention missing --repo"
        fi
    fi
}

# Test: Invalid repo path should fail
test_invalid_repo_path() {
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" --repo "/nonexistent/path" 2>&1); then
        fail_test "Should fail with invalid repo path"
    else
        if [[ "$output" == *"Not a git repo"* ]]; then
            pass_test "Fails correctly with invalid repo path"
        else
            fail_test "Error message should mention not a git repo"
        fi
    fi
}

# Test: Valid repo on feature/* branch should pass
test_valid_feature_branch() {
    setup_test_repo
    git checkout -q -b feature/test-branch
    
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" --repo "$TEST_REPO" 2>&1); then
        if [[ "$output" == *"GUARDRAIL_PASS"* ]]; then
            pass_test "Passes on valid feature/* branch"
        else
            fail_test "Should pass on feature/* branch: $output"
        fi
    else
        fail_test "Should not fail on feature/* branch: $output"
    fi
    cleanup_test_repo
}

# Test: main branch should be blocked
test_main_branch_blocked() {
    setup_test_repo
    git checkout -q -b main
    
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" --repo "$TEST_REPO" 2>&1); then
        fail_test "Should fail on main branch"
    else
        if [[ "$output" == *"GUARDRAIL_FAIL"* && "$output" == *"main"* ]]; then
            pass_test "Blocks direct commits to main branch"
        else
            fail_test "Should fail with GUARDRAIL_FAIL mentioning main: $output"
        fi
    fi
    cleanup_test_repo
}

# Test: master branch should be blocked
test_master_branch_blocked() {
    setup_test_repo
    # master is often the default, rename if needed
    git branch -m master 2>/dev/null || true
    git checkout -q master 2>/dev/null || git checkout -q -b master
    
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" --repo "$TEST_REPO" 2>&1); then
        fail_test "Should fail on master branch"
    else
        if [[ "$output" == *"GUARDRAIL_FAIL"* && "$output" == *"master"* ]]; then
            pass_test "Blocks direct commits to master branch"
        else
            fail_test "Should fail with GUARDRAIL_FAIL mentioning master: $output"
        fi
    fi
    cleanup_test_repo
}

# Test: Non-feature branch should be blocked
test_non_feature_branch_blocked() {
    setup_test_repo
    git checkout -q -b bugfix/something
    
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" --repo "$TEST_REPO" 2>&1); then
        fail_test "Should fail on non-feature branch"
    else
        if [[ "$output" == *"GUARDRAIL_FAIL"* && "$output" == *"feature/"* ]]; then
            pass_test "Blocks non-feature/* branches"
        else
            fail_test "Should mention feature/* requirement: $output"
        fi
    fi
    cleanup_test_repo
}

# Test: --no-branch-check should skip branch validation
test_no_branch_check_flag() {
    setup_test_repo
    git checkout -q -b main
    
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" --repo "$TEST_REPO" --no-branch-check 2>&1); then
        if [[ "$output" == *"GUARDRAIL_PASS"* ]]; then
            pass_test "--no-branch-check skips branch validation"
        else
            fail_test "Should pass with --no-branch-check: $output"
        fi
    else
        fail_test "Should not fail with --no-branch-check: $output"
    fi
    cleanup_test_repo
}

# Test: Help flag works
test_help_flag() {
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" --help 2>&1); then
        if [[ "$output" == *"--repo"* && "$output" == *"feature"* ]]; then
            pass_test "Help flag shows usage information"
        else
            fail_test "Help should mention --repo and feature/*"
        fi
    else
        fail_test "Help flag should succeed"
    fi
}

# Test: Detects test files
test_test_detection() {
    setup_test_repo
    mkdir -p "$TEST_REPO/tests"
    echo "print('test')" > "$TEST_REPO/tests/test_example.py"
    git add tests/test_example.py
    git commit -q -m "Add test file"
    git checkout -q -b feature/test-detection
    
    local output
    if output=$(bash "$GUARDRAIL_SCRIPT" --repo "$TEST_REPO" 2>&1); then
        if [[ "$output" == *"test file(s) detected"* ]]; then
            pass_test "Detects test files in repository"
        else
            warn_test "Test detection message not found: $output"
        fi
    else
        fail_test "Should not fail when detecting tests: $output"
    fi
    cleanup_test_repo
}

# Main test runner
main() {
    echo "=========================================="
    echo "Running coding-workflow-guardrails tests"
    echo "=========================================="
    echo ""
    
    test_script_exists
    test_missing_repo_arg
    test_invalid_repo_path
    test_valid_feature_branch
    test_main_branch_blocked
    test_master_branch_blocked
    test_non_feature_branch_blocked
    test_no_branch_check_flag
    test_help_flag
    test_test_detection
    
    echo ""
    echo "=========================================="
    echo "Test Results: ${GREEN}${TESTS_PASSED} passed${NC}, ${RED}${TESTS_FAILED} failed${NC}"
    echo "=========================================="
    
    if [[ "$TESTS_FAILED" -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

main "$@"
