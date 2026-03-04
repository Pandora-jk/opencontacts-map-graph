package com.opencontacts.shared.coresync

enum class SyncDirection {
    IMPORT,
    EXPORT,
}

data class SyncTask(
    val taskId: String,
    val source: String,
    val target: String,
    val direction: SyncDirection,
    val scheduledAtEpochMs: Long,
)

interface SharedSyncScheduler {
    fun schedule(task: SyncTask)
    fun cancel(taskId: String)
    fun dueTasks(nowEpochMs: Long): List<SyncTask>
}

class InMemorySharedSyncScheduler : SharedSyncScheduler {
    private val tasks = linkedMapOf<String, SyncTask>()

    override fun schedule(task: SyncTask) {
        tasks[task.taskId] = task
    }

    override fun cancel(taskId: String) {
        tasks.remove(taskId)
    }

    override fun dueTasks(nowEpochMs: Long): List<SyncTask> {
        return tasks.values.filter { it.scheduledAtEpochMs <= nowEpochMs }
    }
}
