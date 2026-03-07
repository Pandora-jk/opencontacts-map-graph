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
    fun `scheduler deduplicates by unique name and prevents duplicate claims`() {
        val scheduler = SharedSyncSchedulers.inMemory()
        val first = SyncTask(
            taskId = "1",
            uniqueName = "contacts-import",
            source = "geojson",
            target = "room",
            direction = SyncDirection.IMPORT,
            scheduledAtEpochMs = 100L,
        )
        val replacement = SyncTask(
            taskId = "2",
            uniqueName = "contacts-import",
            source = "geojson",
            target = "room",
            direction = SyncDirection.IMPORT,
            scheduledAtEpochMs = 150L,
        )

        assertEquals(SyncScheduleOutcome.ADDED, scheduler.schedule(first).outcome)
        assertEquals(SyncScheduleOutcome.REPLACED, scheduler.schedule(replacement).outcome)
        assertEquals(listOf(replacement), scheduler.dueTasks(nowEpochMs = 150L))

        assertEquals(true, scheduler.markRunning("2"))
        assertEquals(false, scheduler.markRunning("2"))
        assertEquals(emptyList<SyncTask>(), scheduler.dueTasks(nowEpochMs = 150L))

        scheduler.markSuccess("2")
        assertEquals(emptyList<SyncTask>(), scheduler.dueTasks(nowEpochMs = 150L))
    }

    @Test
    fun `scheduler applies retry backoff and drops exhausted work`() {
        val scheduler = SharedSyncSchedulers.inMemory()
        val task = SyncTask(
            taskId = "1",
            uniqueName = "gallery-export",
            source = "room",
            target = "kml",
            direction = SyncDirection.EXPORT,
            scheduledAtEpochMs = 100L,
            retryPolicy = SyncRetryPolicy(
                maxAttempts = 3,
                initialBackoffMs = 50L,
                backoffMultiplier = 2,
            ),
        )

        scheduler.schedule(task)
        assertEquals(true, scheduler.markRunning("1"))

        val retryOne = scheduler.markFailure(taskId = "1", failedAtEpochMs = 200L)
        assertEquals(250L, retryOne!!.scheduledAtEpochMs)
        assertEquals(1, retryOne.attemptCount)
        assertEquals(emptyList<SyncTask>(), scheduler.dueTasks(nowEpochMs = 249L))
        assertEquals(listOf(retryOne), scheduler.dueTasks(nowEpochMs = 250L))

        assertEquals(true, scheduler.markRunning("1"))
        val retryTwo = scheduler.markFailure(taskId = "1", failedAtEpochMs = 300L)
        assertEquals(400L, retryTwo!!.scheduledAtEpochMs)
        assertEquals(2, retryTwo.attemptCount)

        assertEquals(true, scheduler.markRunning("1"))
        assertEquals(null, scheduler.markFailure(taskId = "1", failedAtEpochMs = 500L))
        assertEquals(emptyList<SyncTask>(), scheduler.dueTasks(nowEpochMs = 1_000L))
    }

    @Test
    fun `scheduler honors runtime constraints`() {
        val scheduler = SharedSyncSchedulers.inMemory()
        val constrained = SyncTask(
            taskId = "1",
            uniqueName = "shared-sync",
            source = "geojson",
            target = "room",
            direction = SyncDirection.IMPORT,
            scheduledAtEpochMs = 100L,
            constraints = SyncConstraints(
                requiresCharging = true,
                requiresBatteryNotLow = true,
                requiredNetwork = SyncNetworkPolicy.UNMETERED,
            ),
        )

        scheduler.schedule(constrained)

        assertEquals(
            emptyList<SyncTask>(),
            scheduler.dueTasks(
                nowEpochMs = 100L,
                runtimeState = SyncRuntimeState(
                    isCharging = false,
                    isBatteryNotLow = true,
                    availableNetwork = SyncNetworkPolicy.UNMETERED,
                ),
            ),
        )
        assertEquals(
            listOf(constrained),
            scheduler.dueTasks(
                nowEpochMs = 100L,
                runtimeState = SyncRuntimeState(
                    isCharging = true,
                    isBatteryNotLow = true,
                    availableNetwork = SyncNetworkPolicy.UNMETERED,
                ),
            ),
        )
    }

    @Test
    fun `dto constructor signatures stay compatible`() {
        assertEquals(
            listOf(
                "taskId:java.lang.String",
                "uniqueName:java.lang.String",
                "source:java.lang.String",
                "target:java.lang.String",
                "direction:com.opencontacts.shared.coresync.SyncDirection",
                "scheduledAtEpochMs:long",
                "constraints:com.opencontacts.shared.coresync.SyncConstraints",
                "retryPolicy:com.opencontacts.shared.coresync.SyncRetryPolicy",
                "attemptCount:int",
            ),
            constructorSignature(SyncTask::class),
        )
        assertEquals(
            listOf(
                "requiresCharging:boolean",
                "requiresBatteryNotLow:boolean",
                "requiredNetwork:com.opencontacts.shared.coresync.SyncNetworkPolicy",
            ),
            constructorSignature(SyncConstraints::class),
        )
        assertEquals(
            listOf(
                "maxAttempts:int",
                "initialBackoffMs:long",
                "backoffMultiplier:int",
            ),
            constructorSignature(SyncRetryPolicy::class),
        )
        assertEquals(
            listOf(
                "isCharging:boolean",
                "isBatteryNotLow:boolean",
                "availableNetwork:com.opencontacts.shared.coresync.SyncNetworkPolicy",
            ),
            constructorSignature(SyncRuntimeState::class),
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
