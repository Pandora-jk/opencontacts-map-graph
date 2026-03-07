package com.opencontacts.shared.coremedia

import kotlin.reflect.KClass
import kotlin.reflect.full.primaryConstructor
import kotlin.reflect.jvm.javaType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Test
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths

class CoreMediaContractsTest {
    @Test
    fun `index stores assets and returns only geotagged media`() {
        val index = SharedMediaIndexes.inMemory()
        val geotagged = MediaAsset("m1", "image/jpeg", "abc", 100L, MediaGeoPoint(1.0, 2.0))
        val plain = MediaAsset("m2", "image/png", "def", 110L, null)

        index.upsert(geotagged)
        index.upsert(plain)

        assertNotNull(index.findByMediaId("m1"))
        assertEquals(listOf(geotagged), index.findGeoTagged())
    }

    @Test
    fun `dto constructor signatures stay compatible`() {
        assertEquals(
            listOf(
                "latitude:double",
                "longitude:double",
            ),
            constructorSignature(MediaGeoPoint::class),
        )
        assertEquals(
            listOf(
                "mediaId:java.lang.String",
                "mimeType:java.lang.String",
                "checksum:java.lang.String",
                "capturedAtEpochMs:java.lang.Long",
                "geoPoint:com.opencontacts.shared.coremedia.MediaGeoPoint",
            ),
            constructorSignature(MediaAsset::class),
        )
    }

    @Test
    fun `factory returns shared interface type`() {
        val method = SharedMediaIndexes::class.java.getDeclaredMethod("inMemory")
        assertEquals(SharedMediaIndex::class.java, method.returnType)
    }

    @Test
    fun `module keeps explicit boundaries`() {
        assertModuleBoundaries(
            moduleName = "core-media",
            anchor = CoreMediaContractsTest::class.java,
            forbiddenImports = listOf(
                "android.",
                "androidx.",
                "com.opencontacts.mapgraph",
                "com.opencontacts.shared.coredb",
                "com.opencontacts.shared.coremap",
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
