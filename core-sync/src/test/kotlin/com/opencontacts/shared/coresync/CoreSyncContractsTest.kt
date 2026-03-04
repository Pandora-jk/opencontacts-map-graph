package com.opencontacts.shared.coresync

import kotlin.test.Test
import kotlin.test.assertEquals

class CoreSyncContractsTest {
    @Test
    fun `scheduler returns due tasks and supports cancellation`() {
        val scheduler = InMemorySharedSyncScheduler()
        val due = SyncTask("1", "geojson", "room", SyncDirection.IMPORT, 100L)
        val later = SyncTask("2", "room", "kml", SyncDirection.EXPORT, 300L)

        scheduler.schedule(due)
        scheduler.schedule(later)

        assertEquals(listOf(due), scheduler.dueTasks(nowEpochMs = 150L))

        scheduler.cancel("1")

        assertEquals(emptyList(), scheduler.dueTasks(nowEpochMs = 150L))
    }
}
