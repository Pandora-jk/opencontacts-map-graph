package com.opencontacts.shared.coredb

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull

class CoreDbContractsTest {
    @Test
    fun `store upserts and filters by bounds`() {
        val store = InMemorySharedGeoStore()
        val inside = GeoRecord("1", "contact-1", "contact", -33.86, 151.20, 100L)
        val outside = GeoRecord("2", "photo-1", "media", 40.71, -74.00, 200L)

        store.upsert(listOf(inside, outside))

        assertNotNull(store.findByRecordId("1"))
        val sydneyBounds = GeoBounds(-34.0, -33.0, 150.0, 152.0)
        assertEquals(listOf(inside), store.queryByBounds(sydneyBounds))
    }
}
