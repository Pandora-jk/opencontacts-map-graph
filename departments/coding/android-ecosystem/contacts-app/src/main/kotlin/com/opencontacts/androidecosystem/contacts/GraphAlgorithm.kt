package com.opencontacts.androidecosystem.contacts

class GraphAlgorithm {
    fun connectionStrength(graph: ConnectionGraph, firstId: String?, secondId: String?): Int {
        val normalizedFirstId = normalize(firstId) ?: return 0
        val normalizedSecondId = normalize(secondId) ?: return 0
        if (!graph.hasNode(normalizedFirstId) || !graph.hasNode(normalizedSecondId)) {
            return 0
        }
        if (normalizedFirstId == normalizedSecondId) {
            return 100
        }

        val directWeight = if (graph.hasEdge(normalizedFirstId, normalizedSecondId)) 50 else 0
        val sharedNeighbors = graph.neighbors(normalizedFirstId).intersect(graph.neighbors(normalizedSecondId)).size
        val sharedWeight = minOf(40, sharedNeighbors * 20)
        val pathWeight = if (directWeight == 0 && sharedWeight == 0 && shortestPathLength(graph, normalizedFirstId, normalizedSecondId) != null) {
            10
        } else {
            0
        }
        return directWeight + sharedWeight + pathWeight
    }

    fun shortestPathLength(graph: ConnectionGraph, firstId: String?, secondId: String?): Int? {
        val normalizedFirstId = normalize(firstId) ?: return null
        val normalizedSecondId = normalize(secondId) ?: return null
        if (!graph.hasNode(normalizedFirstId) || !graph.hasNode(normalizedSecondId)) {
            return null
        }
        if (normalizedFirstId == normalizedSecondId) {
            return 0
        }

        val visited = mutableSetOf(normalizedFirstId)
        val queue = ArrayDeque<Pair<String, Int>>()
        queue.addLast(normalizedFirstId to 0)

        while (queue.isNotEmpty()) {
            val (currentId, depth) = queue.removeFirst()
            for (neighbor in graph.neighbors(currentId)) {
                if (neighbor == normalizedSecondId) {
                    return depth + 1
                }
                if (visited.add(neighbor)) {
                    queue.addLast(neighbor to depth + 1)
                }
            }
        }

        return null
    }

    fun findClusters(graph: ConnectionGraph, minimumSize: Int = 1): List<Set<String>> {
        val normalizedMinimum = minimumSize.coerceAtLeast(1)
        return graph.clusters()
            .filter { it.size >= normalizedMinimum }
            .sortedWith(
                compareByDescending<Set<String>> { it.size }
                    .thenBy { it.sorted().firstOrNull().orEmpty() }
            )
    }

    private fun normalize(id: String?): String? = id?.trim()?.takeIf(String::isNotEmpty)
}
