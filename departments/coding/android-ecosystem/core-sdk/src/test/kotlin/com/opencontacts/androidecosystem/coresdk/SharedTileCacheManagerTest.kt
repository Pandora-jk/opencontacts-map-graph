package com.opencontacts.androidecosystem.coresdk

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SharedTileCacheManagerTest {
    @Test
    fun get_returnsCachedCopy_andMissingTilesReturnNull() {
        val cacheManager = SharedTileCacheManager(maxEntries = 2)
        val tileData = byteArrayOf(1, 2, 3)

        assertTrue(cacheManager.put("tile-a", tileData))

        val cachedTile = cacheManager.get("tile-a")
        assertNotNull(cachedTile)
        assertArrayEquals(byteArrayOf(1, 2, 3), cachedTile)

        cachedTile!![0] = 9
        assertArrayEquals(byteArrayOf(1, 2, 3), cacheManager.get("tile-a"))
        assertNull(cacheManager.get("tile-missing"))
    }

    @Test
    fun put_evictsLeastRecentlyUsedTile() {
        val cacheManager = SharedTileCacheManager(maxEntries = 2)

        cacheManager.put("tile-a", byteArrayOf(1))
        cacheManager.put("tile-b", byteArrayOf(2))
        assertArrayEquals(byteArrayOf(1), cacheManager.get("tile-a"))

        cacheManager.put("tile-c", byteArrayOf(3))

        assertTrue(cacheManager.contains("tile-a"))
        assertFalse(cacheManager.contains("tile-b"))
        assertTrue(cacheManager.contains("tile-c"))
        assertEquals(2, cacheManager.size())
    }

    @Test
    fun put_rejectsInvalidInputs_andConstructorRequiresPositiveCapacity() {
        val cacheManager = SharedTileCacheManager(maxEntries = 2)

        assertFalse(cacheManager.put(null, byteArrayOf(1)))
        assertFalse(cacheManager.put("   ", byteArrayOf(1)))
        assertFalse(cacheManager.put("tile-a", null))
        assertFalse(cacheManager.put("tile-a", byteArrayOf()))
        assertEquals(0, cacheManager.size())

        try {
            SharedTileCacheManager(maxEntries = 0)
        } catch (exception: IllegalArgumentException) {
            assertTrue(exception.message!!.contains("maxEntries"))
            return
        }

        throw AssertionError("Expected IllegalArgumentException for zero-capacity cache")
    }
}
