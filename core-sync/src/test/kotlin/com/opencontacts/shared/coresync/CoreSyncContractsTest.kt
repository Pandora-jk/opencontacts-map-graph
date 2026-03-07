package com.opencontacts.shared.coresync

import kotlin.reflect.KClass
import kotlin.reflect.full.primaryConstructor
import kotlin.reflect.jvm.javaType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths

class CoreSyncContractsTest {
    @Test
    fun `scheduler returns due tasks and supports cancellation`() {
        val scheduler = SharedSyncSchedulers.inMemory()
        val due = SyncTask("1", "geojson", "room", SyncDirection.IMPORT, 100L)
        val later = SyncTask("2", "room", "kml", SyncDirection.EXPORT, 300L)

        scheduler.schedule(due)
        scheduler.schedule(later)

        assertEquals(listOf(due), scheduler.dueTasks(nowEpochMs = 150L))

        scheduler.cancel("1")

        assertEquals(emptyList<SyncTask>(), scheduler.dueTasks(nowEpochMs = 150L))
    }

    @Test
    fun `dto constructor signatures stay compatible`() {
        assertEquals(
            listOf(
                "taskId:java.lang.String",
                "source:java.lang.String",
                "target:java.lang.String",
                "direction:com.opencontacts.shared.coresync.SyncDirection",
                "scheduledAtEpochMs:long",
            ),
            constructorSignature(SyncTask::class),
        )
    }

    @Test
    fun `factory returns shared interface type`() {
        val method = SharedSyncSchedulers::class.java.getDeclaredMethod("inMemory")
        assertEquals(SharedSyncScheduler::class.java, method.returnType)
    }

    @Test
    fun `module keeps explicit boundaries`() {
        assertModuleBoundaries(
            moduleName = "core-sync",
            anchor = CoreSyncContractsTest::class.java,
            forbiddenImports = listOf(
                "android.",
                "androidx.",
                "com.opencontacts.mapgraph",
                "com.opencontacts.shared.coredb",
                "com.opencontacts.shared.coremap",
                "com.opencontacts.shared.coremedia",
            ),
        )
    }

    private fun constructorSignature(type: KClass<*>): List<String> {
        return type.primaryConstructor!!.parameters.map { parameter ->
            "${parameter.name}:${parameter.type.javaType.typeName}"
        }
    }

    private fun assertModuleBoundaries(
        moduleName: String,
        anchor: Class<*>,
        forbiddenImports: List<String>,
    ) {
        val moduleDir = moduleDir(moduleName, anchor)
        val buildText = Files.readString(moduleDir.resolve("build.gradle.kts"))
        assertFalse(
            "Core module should not declare project dependencies",
            buildText.contains("project(\""),
        )

        Files.walk(moduleDir.resolve("src/main/kotlin")).use { paths ->
            paths.filter { Files.isRegularFile(it) }.forEach { path ->
                val content = Files.readString(path)
                forbiddenImports.forEach { prefix ->
                    assertFalse(
                        "Forbidden import '$prefix' in ${moduleDir.relativize(path)}",
                        content.lineSequence().any { line -> line.trim().startsWith("import $prefix") },
                    )
                }
            }
        }
    }

    private fun moduleDir(moduleName: String, anchor: Class<*>): Path {
        val repoRoot = System.getProperty("shared.core.repo.root")
        if (repoRoot != null) {
            return Paths.get(repoRoot, moduleName)
        }

        var path = Paths.get(anchor.protectionDomain.codeSource.location.toURI())
        repeat(4) { path = path.parent }
        return path
    }
}
