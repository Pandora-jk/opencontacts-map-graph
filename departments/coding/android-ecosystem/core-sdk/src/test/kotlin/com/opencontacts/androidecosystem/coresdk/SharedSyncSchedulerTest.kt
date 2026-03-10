package com.opencontacts.androidecosystem.coresdk

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class SharedSyncSchedulerTest {
    private val scheduler = SharedSyncScheduler()

    @Test
    fun schedule_ordersJobsByPriorityThenScheduledTime() {
        val slowJob = SyncJob(id = "slow", scheduledAtEpochMillis = 2000L, priority = 1)
        val urgentJob = SyncJob(id = "urgent", scheduledAtEpochMillis = 3000L, priority = 5)
        val earlierUrgentJob = SyncJob(id = "urgent-early", scheduledAtEpochMillis = 1000L, priority = 5)

        assertTrue(scheduler.schedule(slowJob))
        assertTrue(scheduler.schedule(urgentJob))
        assertTrue(scheduler.schedule(earlierUrgentJob))

        assertEquals(listOf("urgent-early", "urgent", "slow"), scheduler.pendingJobs().map { it.id })
        assertEquals("urgent-early", scheduler.nextJob()!!.id)
    }

    @Test
    fun schedule_deduplicatesJobsAndSupportsCompletion() {
        val job = SyncJob(id = "contacts-full-sync", scheduledAtEpochMillis = 100L, priority = 3)

        assertTrue(scheduler.schedule(job))
        assertFalse(scheduler.schedule(job.copy(priority = 9)))
        assertTrue(scheduler.hasJob("contacts-full-sync"))
        assertEquals(1, scheduler.size())

        assertTrue(scheduler.markCompleted("contacts-full-sync"))
        assertFalse(scheduler.hasJob("contacts-full-sync"))
        assertFalse(scheduler.markCompleted("contacts-full-sync"))
        assertNull(scheduler.nextJob())
    }

    @Test
    fun schedule_rejectsNullAndBlankIds() {
        assertFalse(scheduler.schedule(null))
        assertFalse(scheduler.schedule(SyncJob(id = "   ", scheduledAtEpochMillis = 100L)))
        assertFalse(scheduler.hasJob("   "))
        assertEquals(emptyList<SyncJob>(), scheduler.pendingJobs())
    }
}
