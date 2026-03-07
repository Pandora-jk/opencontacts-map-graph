plugins {
    id("org.jetbrains.kotlin.jvm")
}

kotlin {
    explicitApi()
    jvmToolchain(17)
}

dependencies {
    testImplementation("junit:junit:4.13.2")
    testImplementation(kotlin("reflect"))
}

tasks.test {
    useJUnit()
}
