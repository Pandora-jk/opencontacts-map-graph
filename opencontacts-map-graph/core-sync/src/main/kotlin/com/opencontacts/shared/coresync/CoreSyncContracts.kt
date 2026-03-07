package com.opencontacts.shared.coresync

public enum class SyncDirection {
    IMPORT,
    EXPORT,
}

public data class SyncTask(
    val taskId: String,
    val source: String,
    val target: String,
    val direction: SyncDirection,
    val scheduledAtEpochMs: Long,
)

public interface SharedSyncScheduler {
    public fun schedule(task: SyncTask)
    public fun cancel(taskId: String)
    public fun dueTasks(nowEpochMs: Long): List<SyncTask>
}

public object SharedSyncSchedulers {
    public fun inMemory(): SharedSyncScheduler = InMemorySharedSyncScheduler()
}

internal class InMemorySharedSyncScheduler : SharedSyncScheduler {
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
