package com.opencontacts.shared.coremap

import kotlin.reflect.KClass
import kotlin.reflect.full.primaryConstructor
import kotlin.reflect.jvm.javaType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
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
    }

    @Test
    fun `factory returns shared interface type`() {
        val method = SharedTileCaches::class.java.getDeclaredMethod("inMemory")
        assertEquals(SharedTileCache::class.java, method.returnType)
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
