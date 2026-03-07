#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
KOTLIN_HOME="/opt/gradle/gradle-8.7"
KOTLIN_LIB="$KOTLIN_HOME/lib"
COMPILER_CP="$KOTLIN_LIB/*"
TEST_CP="$KOTLIN_LIB/kotlin-stdlib-1.9.22.jar:$KOTLIN_LIB/kotlin-reflect-1.9.22.jar:$KOTLIN_LIB/junit-4.13.2.jar:$KOTLIN_LIB/hamcrest-core-1.3.jar"
BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/shared-core-contract-tests.XXXXXX")"

cleanup() {
    rm -rf "$BUILD_DIR"
}
trap cleanup EXIT

run_module() {
    local module="$1"
    local test_class="$2"
    local output_dir="$BUILD_DIR/$module"

    mkdir -p "$output_dir"
    mapfile -t sources < <(find "$ROOT_DIR/$module/src/main/kotlin" "$ROOT_DIR/$module/src/test/kotlin" -type f -name '*.kt' | sort)

    java -cp "$COMPILER_CP" org.jetbrains.kotlin.cli.jvm.K2JVMCompiler \
        -kotlin-home "$KOTLIN_HOME" \
        -no-stdlib \
        -no-reflect \
        -cp "$TEST_CP" \
        -d "$output_dir" \
        "${sources[@]}"

    java -Dshared.core.repo.root="$ROOT_DIR" \
        -cp "$output_dir:$TEST_CP" \
        org.junit.runner.JUnitCore "$test_class"
}

run_module "core-db" "com.opencontacts.shared.coredb.CoreDbContractsTest"
run_module "core-map" "com.opencontacts.shared.coremap.CoreMapContractsTest"
run_module "core-media" "com.opencontacts.shared.coremedia.CoreMediaContractsTest"
run_module "core-sync" "com.opencontacts.shared.coresync.CoreSyncContractsTest"
