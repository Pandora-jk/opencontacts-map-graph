package com.openclaw.androidecosystem.contacts.contactsgraph

import com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

class GraphAlgorithm {

    fun buildGraph(
        contacts: List<ContactEntity>,
        interactions: List<ConnectionEdge>
    ): ConnectionGraph {
        val nodes = contacts.associateBy(ContactEntity::id) { ConnectionNode(it) }
        val mergedEdges = interactions
            .filter { nodes.containsKey(it.fromContactId) && nodes.containsKey(it.toContactId) }
            .groupBy { it.normalized().let { edge -> edge.fromContactId to edge.toContactId } }
            .values
            .map { groupedEdges -> groupedEdges.map(ConnectionEdge::normalized).reduce(ConnectionEdge::combine) }

        return ConnectionGraph(nodes = nodes, edges = mergedEdges)
    }

    fun inferGraph(contacts: List<ContactEntity>): ConnectionGraph {
        if (contacts.size < 2) {
            return ConnectionGraph(
                nodes = contacts.associateBy(ContactEntity::id) { ConnectionNode(it) },
                edges = emptyList()
            )
        }

        val rankedContacts = contacts.sortedWith(
            compareByDescending<ContactEntity> { it.connectionStrength }
                .thenByDescending { it.lastContacted ?: 0L }
        )

        val inferredEdges = buildList {
            rankedContacts.windowed(size = 2, step = 1, partialWindows = false).forEach { pair ->
                val first = pair[0]
                val second = pair[1]
                add(
                    ConnectionEdge(
                        fromContactId = first.id,
                        toContactId = second.id,
                        callCount = max(1, (first.connectionStrength + second.connectionStrength) / 30),
                        smsCount = max(0, abs(first.displayName.length - second.displayName.length) % 4),
                        emailCount = if (sameEmailDomain(first, second)) 2 else 0,
                        lastInteraction = max(first.lastContacted ?: 0L, second.lastContacted ?: 0L).takeIf {
                            it > 0L
                        }
                    )
                )
            }
        }

        return buildGraph(rankedContacts, inferredEdges)
    }

    fun calculateConnectionStrength(edge: ConnectionEdge, now: Long = System.currentTimeMillis()): Int {
        val interactionScore = edge.callCount * 5 + edge.smsCount * 3 + edge.emailCount * 2
        val recencyScore = when {
            edge.lastInteraction == null -> 0
            now - edge.lastInteraction <= WEEK_MS -> 25
            now - edge.lastInteraction <= MONTH_MS -> 15
            else -> 5
        }
        return min(100, interactionScore + recencyScore)
    }

    fun findClusters(graph: ConnectionGraph, minimumStrength: Int = 1): List<Set<Long>> {
        val qualifyingEdges = graph.edges.filter { calculateConnectionStrength(it) >= minimumStrength }
        val adjacency = mutableMapOf<Long, MutableSet<Long>>()
        qualifyingEdges.forEach { edge ->
            adjacency.getOrPut(edge.fromContactId) { mutableSetOf() }.add(edge.toContactId)
            adjacency.getOrPut(edge.toContactId) { mutableSetOf() }.add(edge.fromContactId)
        }

        val visited = mutableSetOf<Long>()
        val clusters = mutableListOf<Set<Long>>()

        graph.nodes.keys.forEach { nodeId ->
            if (!visited.add(nodeId)) {
                return@forEach
            }
            val cluster = mutableSetOf<Long>()
            val queue = ArrayDeque<Long>()
            queue += nodeId

            while (queue.isNotEmpty()) {
                val current = queue.removeFirst()
                cluster += current
                adjacency[current].orEmpty().forEach { neighbor ->
                    if (visited.add(neighbor)) {
                        queue += neighbor
                    }
                }
            }
            clusters += cluster
        }

        return clusters.sortedByDescending(Set<Long>::size)
    }

    fun suggestConnections(
        contactId: Long,
        graph: ConnectionGraph,
        limit: Int = 3
    ): List<Long> {
        if (!graph.contains(contactId)) {
            return emptyList()
        }

        val directNeighbors = graph.neighborsOf(contactId)
        val suggestions = directNeighbors
            .flatMap { graph.neighborsOf(it) }
            .filterNot { it == contactId || it in directNeighbors }
            .groupingBy { it }
            .eachCount()

        return suggestions.entries
            .sortedWith(
                compareByDescending<Map.Entry<Long, Int>> { it.value }
                    .thenByDescending { graph.degreeOf(it.key) }
            )
            .take(limit)
            .map { it.key }
    }

    private fun sameEmailDomain(first: ContactEntity, second: ContactEntity): Boolean {
        val firstDomain = first.email?.substringAfter('@', "")
        val secondDomain = second.email?.substringAfter('@', "")
        return !firstDomain.isNullOrBlank() && firstDomain.equals(secondDomain, ignoreCase = true)
    }

    private companion object {
        const val WEEK_MS = 7L * 24L * 60L * 60L * 1000L
        const val MONTH_MS = 30L * 24L * 60L * 60L * 1000L
    }
}
