package com.opencontacts.androidecosystem.coresdk

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SharedGeoStoreTest {
    private val store = SharedGeoStore()

    @Test
    fun putAndGet_storesTrimmedIdAndReturnsCoordinate() {
        val stored = store.put(" home ", 37.4219999, -122.0840575)

        assertTrue(stored)
        assertEquals(1, store.size())
        assertEquals(GeoCoordinate(37.4219999, -122.0840575), store.get("home"))
        assertEquals(mapOf("home" to GeoCoordinate(37.4219999, -122.0840575)), store.all())
    }

    @Test
    fun put_rejectsNullBlankAndInvalidCoordinates() {
        assertFalse(store.put(null, 10.0, 10.0))
        assertFalse(store.put("   ", 10.0, 10.0))
        assertFalse(store.put("missing-lat", null, 10.0))
        assertFalse(store.put("missing-lon", 10.0, null))
        assertFalse(store.put("bad-lat", 91.0, 10.0))
        assertFalse(store.put("bad-lon", 10.0, -181.0))

        assertEquals(0, store.size())
        assertNull(store.get("missing-lat"))
        assertNull(store.get("bad-lon"))
    }

    @Test
    fun removeAndClear_updateStoredEntries() {
        store.put("home", 37.0, -122.0)
        store.put("office", 38.0, -121.0)

        assertTrue(store.remove("home"))
        assertFalse(store.remove("home"))
        assertNull(store.get("home"))
        assertEquals(1, store.size())

        store.clear()

        assertEquals(0, store.size())
        assertTrue(store.all().isEmpty())
    }
}
