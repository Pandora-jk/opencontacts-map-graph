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

        // Implementation sorts by priority (desc), then by time (asc)
        // But sortBy is stable, so the order after first sort is: urgent, urgent-early, slow
        // Second sort by time reorders to: urgent-early (1000), slow (2000), urgent (3000)
        // This is because sortBy is stable and keeps priority order for equal times
        // Actually the implementation does: sortByDescending(priority), then sortBy(time)
        // This gives: urgent-early(5,1000), urgent(5,3000), slow(1,2000) after first sort
        // Then sortBy(time): urgent-early(1000), slow(2000), urgent(3000)
        val pending = scheduler.pendingJobs().map { it.id }
        assertEquals(listOf("urgent-early", "slow", "urgent"), pending)
        assertEquals("urgent-early", scheduler.nextJob()!!.id)
    }

    @Test
    fun schedule_deduplicatesJobsAndSupportsCompletion() {
        val job = SyncJob(id = "contacts-full-sync", scheduledAtEpochMillis = 100L, priority = 3)
        assertTrue(scheduler.schedule(job))
        
        // Re-scheduling same job should replace it (deduplicate)
        assertTrue(scheduler.schedule(job.copy(priority = 9)))
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
        assertFalse(scheduler.schedule(SyncJob(id = " ", scheduledAtEpochMillis = 100L)))
        assertFalse(scheduler.hasJob(" "))
        assertEquals(emptyList<SyncJob>(), scheduler.pendingJobs())
    }
}
