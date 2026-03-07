package com.opencontacts.shared.coremap

import kotlin.reflect.KClass
import kotlin.reflect.full.primaryConstructor
import kotlin.reflect.jvm.javaType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertSame
import org.junit.Assert.assertTrue
import org.junit.Test
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths

class CoreMapContractsTest {
    @Test
    fun `cache supports read write remove contract`() {
        val cache = SharedTileCaches.inMemory()
        val key = MapTileKey(10, 945, 612, "default")
        val payload = MapTilePayload(byteArrayOf(1, 2, 3), "etag", 123L)

        cache.write(key, payload)

        assertNotNull(cache.read(key))
        assertEquals(1, cache.size())

        cache.remove(key)

        assertNull(cache.read(key))
        assertEquals(0, cache.size())
    }

    @Test
    fun `manager caches remote fetches and records hit miss stats`() {
        val manager = SharedTileCaches.manager(maxEntries = 2)
        val key = MapTileKey(4, 8, 12, "streets")
        val payload = MapTilePayload(byteArrayOf(9, 9), "etag-1", 200L)
        var remoteFetches = 0

        val first = manager.load(key) {
            remoteFetches += 1
            payload
        }
        val second = manager.load(key) {
            remoteFetches += 1
            MapTilePayload(byteArrayOf(1), "etag-2", 300L)
        }

        assertNotNull(first)
        assertEquals(MapTileSource.REMOTE, first!!.source)
        assertNotNull(second)
        assertEquals(MapTileSource.CACHE, second!!.source)
        assertSame(first.payload, second.payload)
        assertEquals(1, remoteFetches)
        assertEquals(MapTileCacheStats(hits = 1, misses = 1, evictions = 0), manager.stats())
    }

    @Test
    fun `manager evicts least recently used tile when capacity is exceeded`() {
        val manager = SharedTileCaches.manager(maxEntries = 2)
        val tileA = MapTileKey(1, 1, 1, "default")
        val tileB = MapTileKey(1, 1, 2, "default")
        val tileC = MapTileKey(1, 1, 3, "default")

        manager.write(tileA, MapTilePayload(byteArrayOf(1), null, 10L))
        manager.write(tileB, MapTilePayload(byteArrayOf(2), null, 20L))
        assertNotNull(manager.read(tileA))

        manager.write(tileC, MapTilePayload(byteArrayOf(3), null, 30L))

        assertNotNull(manager.read(tileA))
        assertNull(manager.read(tileB))
        assertNotNull(manager.read(tileC))
        assertEquals(2, manager.size())
        assertEquals(MapTileCacheStats(hits = 0, misses = 0, evictions = 1), manager.stats())
    }

    @Test
    fun `manager supports offline cache reads without remote fetch`() {
        val manager = SharedTileCaches.manager(maxEntries = 2)
        val cachedKey = MapTileKey(9, 22, 40, "satellite")
        val cached = MapTilePayload(byteArrayOf(4, 5, 6), "etag-offline", 500L)

        manager.write(cachedKey, cached)

        assertSame(cached, manager.readOffline(cachedKey))
        assertNull(manager.readOffline(MapTileKey(9, 22, 41, "satellite")))
        assertEquals(MapTileCacheStats(hits = 1, misses = 1, evictions = 0), manager.stats())
    }

    @Test
    fun `dto constructor signatures stay compatible`() {
        assertEquals(
            listOf(
                "zoom:int",
                "x:int",
                "y:int",
                "style:java.lang.String",
            ),
            constructorSignature(MapTileKey::class),
        )
        assertEquals(
            listOf(
                "bytes:byte[]",
                "etag:java.lang.String",
                "fetchedAtEpochMs:long",
            ),
            constructorSignature(MapTilePayload::class),
        )
        assertEquals(
            listOf(
                "hits:int",
                "misses:int",
                "evictions:int",
            ),
            constructorSignature(MapTileCacheStats::class),
        )
        assertEquals(
            listOf(
                "payload:com.opencontacts.shared.coremap.MapTilePayload",
                "source:com.opencontacts.shared.coremap.MapTileSource",
            ),
            constructorSignature(MapTileLoadResult::class),
        )
    }

    @Test
    fun `factory returns shared interface type`() {
        val method = SharedTileCaches::class.java.getDeclaredMethod("inMemory")
        assertEquals(SharedTileCache::class.java, method.returnType)
        val managerMethod = SharedTileCaches::class.java.getDeclaredMethod("manager", Int::class.javaPrimitiveType)
        assertEquals(SharedTileCacheManager::class.java, managerMethod.returnType)
        assertTrue(SharedTileCaches.DEFAULT_MAX_ENTRIES > 0)
    }

    @Test
    fun `module keeps explicit boundaries`() {
        assertModuleBoundaries(
            moduleName = "core-map",
            anchor = CoreMapContractsTest::class.java,
            forbiddenImports = listOf(
                "android.",
                "androidx.",
                "com.opencontacts.mapgraph",
                "com.opencontacts.shared.coredb",
                "com.opencontacts.shared.coremedia",
                "com.opencontacts.shared.coresync",
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
        assertTrue("Core module should enable Kotlin explicit API mode", buildText.contains("explicitApi()"))

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
