package com.opencontacts.shared.coremedia

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull

class CoreMediaContractsTest {
    @Test
    fun `index stores assets and returns only geotagged media`() {
        val index = InMemorySharedMediaIndex()
        val geotagged = MediaAsset("m1", "image/jpeg", "abc", 100L, MediaGeoPoint(1.0, 2.0))
        val plain = MediaAsset("m2", "image/png", "def", 110L, null)

        index.upsert(geotagged)
        index.upsert(plain)

        assertNotNull(index.findByMediaId("m1"))
        assertEquals(listOf(geotagged), index.findGeoTagged())
    }
}
