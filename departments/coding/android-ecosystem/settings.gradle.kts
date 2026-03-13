pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

// Apps
include(":apps:contacts")
// include(":apps:gallery")  // Future
// include(":apps:dialer")   // Future

// Core Libraries
include(":core:database")
include(":core:map")
include(":core:media")
include(":core:sync")

// Legacy (to be removed after migration)
// include(":contacts-app")
// include(":core-sdk")
// include(":gallery-app")
