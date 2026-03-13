package com.opencontacts.androidecosystem.contacts

class ConnectionGraph {
    private val adjacency = linkedMapOf<String, LinkedHashSet<String>>()

    fun addNode(id: String?): Boolean {
        val normalizedId = normalize(id) ?: return false
        if (normalizedId in adjacency) {
            return false
        }

        adjacency[normalizedId] = linkedSetOf()
        return true
    }

    fun removeNode(id: String?): Boolean {
        val normalizedId = normalize(id) ?: return false
        val neighbors = adjacency.remove(normalizedId) ?: return false
        neighbors.forEach { neighbor ->
            adjacency[neighbor]?.remove(normalizedId)
        }
        return true
    }

    fun addEdge(firstId: String?, secondId: String?): Boolean {
        val normalizedFirstId = normalize(firstId) ?: return false
        val normalizedSecondId = normalize(secondId) ?: return false
        if (normalizedFirstId == normalizedSecondId) {
            return false
        }

        adjacency.getOrPut(normalizedFirstId) { linkedSetOf() }
        adjacency.getOrPut(normalizedSecondId) { linkedSetOf() }

        val added = adjacency.getValue(normalizedFirstId).add(normalizedSecondId)
        adjacency.getValue(normalizedSecondId).add(normalizedFirstId)
        return added
    }

    fun removeEdge(firstId: String?, secondId: String?): Boolean {
        val normalizedFirstId = normalize(firstId) ?: return false
        val normalizedSecondId = normalize(secondId) ?: return false
        val removedFromFirst = adjacency[normalizedFirstId]?.remove(normalizedSecondId) ?: false
        val removedFromSecond = adjacency[normalizedSecondId]?.remove(normalizedFirstId) ?: false
        return removedFromFirst || removedFromSecond
    }

    fun hasNode(id: String?): Boolean {
        return normalize(id)?.let(adjacency::containsKey) == true
    }

    fun hasEdge(firstId: String?, secondId: String?): Boolean {
        val normalizedFirstId = normalize(firstId) ?: return false
        val normalizedSecondId = normalize(secondId) ?: return false
        return adjacency[normalizedFirstId]?.contains(normalizedSecondId) == true
    }

    fun neighbors(id: String?): Set<String> {
        val normalizedId = normalize(id) ?: return emptySet()
        return adjacency[normalizedId]?.toSet().orEmpty()
    }

    fun nodes(): Set<String> = adjacency.keys.toCollection(linkedSetOf())

    fun edgeCount(): Int = adjacency.values.sumOf { it.size } / 2

    fun asMap(): Map<String, Set<String>> = adjacency.mapValues { (_, neighbors) -> neighbors.toSet() }

    fun clusters(): List<Set<String>> {
        val visited = mutableSetOf<String>()
        val clusters = mutableListOf<Set<String>>()

        for (node in adjacency.keys) {
            if (!visited.add(node)) {
                continue
            }

            val cluster = linkedSetOf<String>()
            val queue = ArrayDeque<String>()
            queue.addLast(node)

            while (queue.isNotEmpty()) {
                val current = queue.removeFirst()
                cluster.add(current)
                adjacency[current].orEmpty().forEach { neighbor ->
                    if (visited.add(neighbor)) {
                        queue.addLast(neighbor)
                    }
                }
            }

            clusters += cluster
        }

        return clusters
    }

    private fun normalize(id: String?): String? = id?.trim()?.takeIf(String::isNotEmpty)

    companion object {
        fun fromAdjacency(adjacency: Map<String, Set<String>>?): ConnectionGraph {
            val graph = ConnectionGraph()
            adjacency.orEmpty().forEach { (node, neighbors) ->
                graph.addNode(node)
                neighbors.forEach { neighbor ->
                    graph.addEdge(node, neighbor)
                }
            }
            return graph
        }
    }
}
