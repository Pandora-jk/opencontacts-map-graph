package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class GraphAlgorithmTest {
    private val algorithm = GraphAlgorithm()

    @Test
    fun connectionStrength_returnsZeroForBlankIds() {
        val graph = graphOf(edges = arrayOf("alice" to "bob"))

        assertEquals(0, algorithm.connectionStrength(graph, " ", "bob"))
        assertEquals(0, algorithm.connectionStrength(graph, "alice", null))
    }

    @Test
    fun connectionStrength_returnsZeroForUnknownNodes() {
        val graph = graphOf(edges = arrayOf("alice" to "bob"))

        assertEquals(0, algorithm.connectionStrength(graph, "alice", "carol"))
    }

    @Test
    fun connectionStrength_returnsHundredForSameNode() {
        val graph = graphOf(nodes = listOf("alice"))

        assertEquals(100, algorithm.connectionStrength(graph, "alice", "alice"))
    }

    @Test
    fun connectionStrength_returnsFiftyForDirectConnections() {
        val graph = graphOf(edges = arrayOf("alice" to "bob"))

        assertEquals(50, algorithm.connectionStrength(graph, "alice", "bob"))
    }

    @Test
    fun connectionStrength_addsWeightForSharedNeighbors() {
        val graph = graphOf(edges = arrayOf("alice" to "bob", "alice" to "carol", "bob" to "carol"))

        assertEquals(70, algorithm.connectionStrength(graph, "alice", "bob"))
    }

    @Test
    fun connectionStrength_capsSharedNeighborWeightAtForty() {
        val graph = graphOf(
            edges = arrayOf(
                "alice" to "carol",
                "alice" to "dave",
                "alice" to "erin",
                "bob" to "carol",
                "bob" to "dave",
                "bob" to "erin",
            )
        )

        assertEquals(40, algorithm.connectionStrength(graph, "alice", "bob"))
    }

    @Test
    fun connectionStrength_returnsPathWeightForIndirectConnectionsWithoutSharedNeighbors() {
        val graph = graphOf(edges = arrayOf("alice" to "carol", "carol" to "bob"))

        assertEquals(10, algorithm.connectionStrength(graph, "alice", "bob"))
    }

    @Test
    fun connectionStrength_returnsZeroForDisconnectedNodes() {
        val graph = graphOf(nodes = listOf("alice", "bob"))

        assertEquals(0, algorithm.connectionStrength(graph, "alice", "bob"))
    }

    @Test
    fun shortestPathLength_returnsNullForDisconnectedNodes() {
        val graph = graphOf(nodes = listOf("alice", "bob"))

        assertNull(algorithm.shortestPathLength(graph, "alice", "bob"))
    }

    @Test
    fun shortestPathLength_returnsExpectedLengthAcrossChain() {
        val graph = graphOf(edges = arrayOf("alice" to "carol", "carol" to "dave", "dave" to "bob"))

        assertEquals(3, algorithm.shortestPathLength(graph, "alice", "bob"))
    }

    @Test
    fun shortestPathLength_handlesCycles() {
        val graph = graphOf(edges = arrayOf("alice" to "bob", "bob" to "carol", "carol" to "alice"))

        assertEquals(1, algorithm.shortestPathLength(graph, "alice", "carol"))
    }

    @Test
    fun findClusters_filtersByMinimumSize() {
        val graph = graphOf(
            nodes = listOf("solo"),
            edges = arrayOf("alice" to "bob", "bob" to "carol"),
        )

        assertEquals(listOf(setOf("alice", "bob", "carol")), algorithm.findClusters(graph, minimumSize = 2))
    }

    @Test
    fun findClusters_sortsClustersBySizeDescending() {
        val graph = graphOf(
            edges = arrayOf("alice" to "bob", "bob" to "carol", "dave" to "erin"),
        )

        assertEquals(listOf(3, 2), algorithm.findClusters(graph).map { it.size })
    }

    @Test
    fun findClusters_coercesMinimumSizeBelowOne() {
        val graph = graphOf(nodes = listOf("alice"))

        assertEquals(listOf(setOf("alice")), algorithm.findClusters(graph, minimumSize = 0))
    }

    @Test
    fun findClusters_returnsEmptyListForEmptyGraph() {
        assertEquals(emptyList<Set<String>>(), algorithm.findClusters(ConnectionGraph()))
    }
}
