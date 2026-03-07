package com.opencontacts.shared.coredb

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

class CoreDbContractsTest {
    @Test
    fun `store upserts and filters by bounds`() {
        val store = SharedGeoStores.inMemory()
        val inside = GeoRecord("1", "contact-1", "contact", -33.86, 151.20, 100L)
        val outside = GeoRecord("2", "photo-1", "media", 40.71, -74.00, 200L)

        store.upsert(listOf(inside, outside))

        assertNotNull(store.findByRecordId("1"))
        val sydneyBounds = GeoBounds(-34.0, -33.0, 150.0, 152.0)
        assertEquals(listOf(inside), store.queryByBounds(sydneyBounds))
    }

    @Test
    fun `dto constructor signatures stay compatible`() {
        assertEquals(
            listOf(
                "recordId:java.lang.String",
                "sourceId:java.lang.String",
                "sourceType:java.lang.String",
                "latitude:double",
                "longitude:double",
                "updatedAtEpochMs:long",
            ),
            constructorSignature(GeoRecord::class),
        )
        assertEquals(
            listOf(
                "minLatitude:double",
                "maxLatitude:double",
                "minLongitude:double",
                "maxLongitude:double",
            ),
            constructorSignature(GeoBounds::class),
        )
    }

    @Test
    fun `factory returns shared interface type`() {
        val method = SharedGeoStores::class.java.getDeclaredMethod("inMemory")
        assertEquals(SharedGeoStore::class.java, method.returnType)
    }

    @Test
    fun `module keeps explicit boundaries`() {
        assertModuleBoundaries(
            moduleName = "core-db",
            anchor = CoreDbContractsTest::class.java,
            forbiddenImports = listOf(
                "android.",
                "androidx.",
                "com.opencontacts.mapgraph",
                "com.opencontacts.shared.coremap",
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
