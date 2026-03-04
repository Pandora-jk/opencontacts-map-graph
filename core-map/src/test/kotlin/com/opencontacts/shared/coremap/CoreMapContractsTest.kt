package com.opencontacts.shared.coremap

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull

class CoreMapContractsTest {
    @Test
    fun `cache supports read write remove contract`() {
        val cache = InMemorySharedTileCache()
        val key = MapTileKey(10, 945, 612, "default")
        val payload = MapTilePayload(byteArrayOf(1, 2, 3), "etag", 123L)

        cache.write(key, payload)

        assertNotNull(cache.read(key))
        assertEquals(1, cache.size())

        cache.remove(key)

        assertNull(cache.read(key))
        assertEquals(0, cache.size())
    }
}
