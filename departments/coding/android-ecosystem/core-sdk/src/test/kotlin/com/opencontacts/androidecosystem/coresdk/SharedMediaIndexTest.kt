package com.opencontacts.androidecosystem.coresdk

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SharedMediaIndexTest {
    @Test
    fun upsert_addsMediaAsset_andFindByMediaIdReturnsIt() {
        val index = SharedMediaIndex()
        val asset = MediaAsset(
            mediaId = "photo-001",
            mimeType = "image/jpeg",
            checksum = "abc123",
            capturedAtEpochMs = 1000L,
            geoPoint = GeoCoordinate(latitude = 37.7749, longitude = -122.4194)
        )

        index.upsert(asset)

        val found = index.findByMediaId("photo-001")
        assertNotNull(found)
        assertEquals("photo-001", found?.mediaId)
        assertEquals("image/jpeg", found?.mimeType)
    }

    @Test
    fun findGeoTagged_returnsOnlyAssetsWithGeoPoints() {
        val index = SharedMediaIndex()
        index.upsert(
            MediaAsset(
                mediaId = "photo-geo",
                mimeType = "image/jpeg",
                checksum = "xyz",
                capturedAtEpochMs = 2000L,
                geoPoint = GeoCoordinate(latitude = 40.7128, longitude = -74.0060)
            )
        )
        index.upsert(
            MediaAsset(
                mediaId = "photo-no-geo",
                mimeType = "image/png",
                checksum = "def",
                capturedAtEpochMs = 3000L,
                geoPoint = null
            )
        )

        val geoTagged = index.findGeoTagged()

        assertEquals(1, geoTagged.size)
        assertEquals("photo-geo", geoTagged.first().mediaId)
    }

    @Test
    fun remove_deletesMediaAsset_andReturnsFalseForMissing() {
        val index = SharedMediaIndex()
        val asset = MediaAsset(
            mediaId = "to-remove",
            mimeType = "image/gif",
            checksum = "remove-me",
            capturedAtEpochMs = 4000L,
            geoPoint = null
        )

        index.upsert(asset)
        assertTrue(index.remove("to-remove"))
        assertNull(index.findByMediaId("to-remove"))
        assertFalse(index.remove("to-remove"))
    }

    @Test
    fun size_andClear_workCorrectly() {
        val index = SharedMediaIndex()

        assertEquals(0, index.size())

        index.upsert(
            MediaAsset("a", "img/jpg", "1", 1L, null)
        )
        index.upsert(
            MediaAsset("b", "img/png", "2", 2L, null)
        )
        assertEquals(2, index.size())

        index.clear()
        assertEquals(0, index.size())
        assertNull(index.findByMediaId("a"))
    }

    @Test
    fun upsert_handlesNullInput_gracefully() {
        val index = SharedMediaIndex()
        index.upsert(null)
        assertEquals(0, index.size())
    }

    @Test
    fun findByMediaId_handlesNullAndBlankInputs() {
        val index = SharedMediaIndex()
        assertNull(index.findByMediaId(null))
        assertNull(index.findByMediaId(""))
        assertNull(index.findByMediaId("   "))
    }
}
