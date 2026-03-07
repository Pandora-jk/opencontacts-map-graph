package com.opencontacts.shared.coresync

public enum class SyncDirection {
    IMPORT,
    EXPORT,
}

public enum class SyncNetworkPolicy {
    NONE,
    CONNECTED,
    UNMETERED,
}

public data class SyncConstraints(
    val requiresCharging: Boolean = false,
    val requiresBatteryNotLow: Boolean = true,
    val requiredNetwork: SyncNetworkPolicy = SyncNetworkPolicy.CONNECTED,
)

public data class SyncRetryPolicy(
    val maxAttempts: Int = DEFAULT_MAX_ATTEMPTS,
    val initialBackoffMs: Long = DEFAULT_INITIAL_BACKOFF_MS,
    val backoffMultiplier: Int = DEFAULT_BACKOFF_MULTIPLIER,
) {
    init {
        require(maxAttempts > 0) { "maxAttempts must be > 0" }
        require(initialBackoffMs >= 0L) { "initialBackoffMs must be >= 0" }
        require(backoffMultiplier > 0) { "backoffMultiplier must be > 0" }
    }

    internal fun nextScheduledAt(currentAttempt: Int, failedAtEpochMs: Long): Long {
        var delay = initialBackoffMs
        repeat(currentAttempt) {
            delay = delay.coerceAtMost(Long.MAX_VALUE / backoffMultiplier) * backoffMultiplier
        }
        return failedAtEpochMs + delay
    }

    public companion object {
        public const val DEFAULT_MAX_ATTEMPTS: Int = 3
        public const val DEFAULT_INITIAL_BACKOFF_MS: Long = 30_000L
        public const val DEFAULT_BACKOFF_MULTIPLIER: Int = 2
    }
}

public data class SyncRuntimeState(
    val isCharging: Boolean = false,
    val isBatteryNotLow: Boolean = true,
    val availableNetwork: SyncNetworkPolicy = SyncNetworkPolicy.CONNECTED,
)

public data class SyncTask(
    val taskId: String,
    val uniqueName: String,
    val source: String,
    val target: String,
    val direction: SyncDirection,
    val scheduledAtEpochMs: Long,
    val constraints: SyncConstraints = SyncConstraints(),
    val retryPolicy: SyncRetryPolicy = SyncRetryPolicy(),
    val attemptCount: Int = 0,
)

public enum class SyncScheduleOutcome {
    ADDED,
    REPLACED,
    KEPT_EXISTING,
}

public data class SyncScheduleResult(
    val outcome: SyncScheduleOutcome,
    val task: SyncTask,
)

public interface SharedSyncScheduler {
    public fun schedule(task: SyncTask): SyncScheduleResult
    public fun cancel(taskId: String)
    public fun dueTasks(
        nowEpochMs: Long,
        runtimeState: SyncRuntimeState = SyncRuntimeState(),
    ): List<SyncTask>
    public fun markRunning(taskId: String): Boolean
    public fun markSuccess(taskId: String)
    public fun markFailure(taskId: String, failedAtEpochMs: Long): SyncTask?
}

public object SharedSyncSchedulers {
    public fun inMemory(): SharedSyncScheduler = InMemorySharedSyncScheduler()
}

internal class InMemorySharedSyncScheduler : SharedSyncScheduler {
    private val tasksById = linkedMapOf<String, SyncTask>()
    private val taskIdByUniqueName = linkedMapOf<String, String>()
    private val runningTaskIds = linkedSetOf<String>()

    override fun schedule(task: SyncTask): SyncScheduleResult {
        require(task.taskId.isNotBlank()) { "taskId must not be blank" }
        require(task.uniqueName.isNotBlank()) { "uniqueName must not be blank" }
        require(task.source.isNotBlank()) { "source must not be blank" }
        require(task.target.isNotBlank()) { "target must not be blank" }
        require(task.attemptCount >= 0) { "attemptCount must be >= 0" }

        val existingTaskId = taskIdByUniqueName[task.uniqueName]
        if (existingTaskId != null) {
            val existingTask = tasksById[existingTaskId]
            if (existingTask != null) {
                if (runningTaskIds.contains(existingTaskId)) {
                    return SyncScheduleResult(
                        outcome = SyncScheduleOutcome.KEPT_EXISTING,
                        task = existingTask,
                    )
                }
                removeTask(existingTaskId)
                putTask(task)
                return SyncScheduleResult(
                    outcome = SyncScheduleOutcome.REPLACED,
                    task = task,
                )
            }
        }

        putTask(task)
        return SyncScheduleResult(
            outcome = SyncScheduleOutcome.ADDED,
            task = task,
        )
    }

    override fun cancel(taskId: String) {
        removeTask(taskId)
    }

    override fun dueTasks(
        nowEpochMs: Long,
        runtimeState: SyncRuntimeState,
    ): List<SyncTask> {
        return tasksById.values.filter { task ->
            task.scheduledAtEpochMs <= nowEpochMs &&
                !runningTaskIds.contains(task.taskId) &&
                constraintsSatisfied(task.constraints, runtimeState)
        }
    }

    override fun markRunning(taskId: String): Boolean {
        if (!tasksById.containsKey(taskId) || runningTaskIds.contains(taskId)) {
            return false
        }
        runningTaskIds.add(taskId)
        return true
    }

    override fun markSuccess(taskId: String) {
        removeTask(taskId)
    }

    override fun markFailure(taskId: String, failedAtEpochMs: Long): SyncTask? {
        val task = tasksById[taskId] ?: return null
        runningTaskIds.remove(taskId)

        val nextAttempt = task.attemptCount + 1
        if (nextAttempt >= task.retryPolicy.maxAttempts) {
            removeTask(taskId)
            return null
        }

        val retryTask = task.copy(
            scheduledAtEpochMs = task.retryPolicy.nextScheduledAt(
                currentAttempt = task.attemptCount,
                failedAtEpochMs = failedAtEpochMs,
            ),
            attemptCount = nextAttempt,
        )
        tasksById[taskId] = retryTask
        return retryTask
    }

    private fun putTask(task: SyncTask) {
        tasksById[task.taskId] = task
        taskIdByUniqueName[task.uniqueName] = task.taskId
    }

    private fun removeTask(taskId: String) {
        val removed = tasksById.remove(taskId) ?: return
        runningTaskIds.remove(taskId)
        taskIdByUniqueName.remove(removed.uniqueName)
    }

    private fun constraintsSatisfied(
        constraints: SyncConstraints,
        runtimeState: SyncRuntimeState,
    ): Boolean {
        if (constraints.requiresCharging && !runtimeState.isCharging) {
            return false
        }
        if (constraints.requiresBatteryNotLow && !runtimeState.isBatteryNotLow) {
            return false
        }
        return when (constraints.requiredNetwork) {
            SyncNetworkPolicy.NONE -> true
            SyncNetworkPolicy.CONNECTED -> runtimeState.availableNetwork != SyncNetworkPolicy.NONE
            SyncNetworkPolicy.UNMETERED -> runtimeState.availableNetwork == SyncNetworkPolicy.UNMETERED
        }
    }
}
