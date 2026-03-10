package com.opencontacts.androidecosystem.coresdk

data class SyncJob(
    val id: String,
    val scheduledAtEpochMillis: Long,
    val priority: Int = 5,
)

class SharedSyncScheduler {
    private val jobs = mutableListOf<SyncJob>()

    fun schedule(job: SyncJob?): Boolean {
        if (job == null || job.id.isBlank()) return false
        
        jobs.removeAll { it.id == job.id }
        jobs.add(job)
        jobs.sortByDescending { it.priority }
        jobs.sortBy { it.scheduledAtEpochMillis }
        
        return true
    }

    fun nextJob(): SyncJob? = jobs.firstOrNull()

    fun pendingJobs(): List<SyncJob> = jobs.sortedBy { it.scheduledAtEpochMillis }

    fun hasJob(jobId: String?): Boolean {
        if (jobId.isNullOrBlank()) return false
        return jobs.any { it.id == jobId }
    }

    fun markCompleted(jobId: String?): Boolean {
        if (jobId.isNullOrBlank()) return false
        return jobs.removeAll { it.id == jobId }
    }

    fun size(): Int = jobs.size

    fun clear() {
        jobs.clear()
    }
}
