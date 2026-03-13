// Root project build configuration for Android Ecosystem Monorepo
// This is the parent build script for all modules

plugins {
    id("com.android.application") version "8.2.0" apply false
    id("com.android.library") version "8.2.0" apply false
    id("org.jetbrains.kotlin.android") version "1.9.20" apply false
    id("org.jetbrains.kotlin.plugin.serialization") version "1.9.20" apply false
}

tasks.register("clean", Delete::class) {
    delete(rootProject.layout.buildDirectory)
}

// Task to build all apps
tasks.register("buildAll") {
    dependsOn(":apps:contacts:assembleDebug")
    // Add other apps as they are created
}

// Task to test all modules
tasks.register("testAll") {
    dependsOn(":apps:contacts:testDebugUnitTest")
    dependsOn(":core:database:testDebugUnitTest")
    dependsOn(":core:map:testDebugUnitTest")
    dependsOn(":core:media:testDebugUnitTest")
    dependsOn(":core:sync:testDebugUnitTest")
}
