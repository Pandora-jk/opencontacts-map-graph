package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ConnectionGraphTest {
    @Test
    fun addNode_addsTrimmedNodeId() {
        val graph = ConnectionGraph()

        assertTrue(graph.addNode(" alice "))
        assertTrue(graph.hasNode("alice"))
        assertEquals(listOf("alice"), graph.nodes().toList())
    }

    @Test
    fun addNode_returnsFalseForDuplicateNode() {
        val graph = ConnectionGraph()
        graph.addNode("alice")

        assertFalse(graph.addNode(" alice "))
    }

    @Test
    fun addNode_rejectsNullIds() {
        assertFalse(ConnectionGraph().addNode(null))
    }

    @Test
    fun addNode_rejectsBlankIds() {
        assertFalse(ConnectionGraph().addNode("   "))
    }

    @Test
    fun addEdge_createsMissingNodesAutomatically() {
        val graph = ConnectionGraph()

        assertTrue(graph.addEdge("alice", "bob"))
        assertEquals(setOf("alice", "bob"), graph.nodes())
    }

    @Test
    fun addEdge_addsBidirectionalNeighbors() {
        val graph = ConnectionGraph()

        graph.addEdge("alice", "bob")

        assertEquals(setOf("bob"), graph.neighbors("alice"))
        assertEquals(setOf("alice"), graph.neighbors("bob"))
    }

    @Test
    fun addEdge_returnsFalseWhenEdgeAlreadyExists() {
        val graph = ConnectionGraph()
        graph.addEdge("alice", "bob")

        assertFalse(graph.addEdge("bob", "alice"))
    }

    @Test
    fun addEdge_rejectsSelfEdges() {
        assertFalse(ConnectionGraph().addEdge("alice", "alice"))
    }

    @Test
    fun addEdge_rejectsBlankEndpoints() {
        val graph = ConnectionGraph()

        assertFalse(graph.addEdge("alice", " "))
        assertFalse(graph.addEdge(" ", "bob"))
    }

    @Test
    fun removeEdge_removesBothDirections() {
        val graph = graphOf(edges = arrayOf("alice" to "bob"))

        assertTrue(graph.removeEdge("alice", "bob"))
        assertFalse(graph.hasEdge("alice", "bob"))
        assertFalse(graph.hasEdge("bob", "alice"))
    }

    @Test
    fun removeEdge_returnsFalseWhenMissing() {
        val graph = graphOf(edges = arrayOf("alice" to "bob"))

        assertFalse(graph.removeEdge("alice", "carol"))
    }

    @Test
    fun removeNode_removesIncidentEdges() {
        val graph = graphOf(edges = arrayOf("alice" to "bob", "bob" to "carol"))

        assertTrue(graph.removeNode("bob"))

        assertEquals(emptySet<String>(), graph.neighbors("alice"))
        assertEquals(emptySet<String>(), graph.neighbors("carol"))
    }

    @Test
    fun removeNode_returnsFalseForUnknownNode() {
        assertFalse(ConnectionGraph().removeNode("missing"))
    }

    @Test
    fun neighbors_returnsEmptySetForUnknownNode() {
        assertEquals(emptySet<String>(), ConnectionGraph().neighbors("missing"))
    }

    @Test
    fun edgeCount_countsUndirectedEdgesOnce() {
        val graph = graphOf(edges = arrayOf("alice" to "bob", "bob" to "carol"))

        assertEquals(2, graph.edgeCount())
    }

    @Test
    fun clusters_returnsSingleNodeClustersForDisconnectedNodes() {
        val graph = graphOf(nodes = listOf("alice", "bob"))

        assertEquals(listOf(setOf("alice"), setOf("bob")), graph.clusters())
    }

    @Test
    fun clusters_groupsConnectedComponents() {
        val graph = graphOf(
            nodes = listOf("solo"),
            edges = arrayOf("alice" to "bob", "carol" to "dave"),
        )

        assertEquals(
            listOf(setOf("solo"), setOf("alice", "bob"), setOf("carol", "dave")),
            graph.clusters().sortedBy { it.size }
        )
    }

    @Test
    fun fromAdjacency_ignoresBlankNodesAndSelfEdges() {
        val graph = ConnectionGraph.fromAdjacency(
            mapOf(
                "alice" to setOf("alice", "bob"),
                " " to setOf("carol"),
            )
        )

        assertTrue(graph.hasEdge("alice", "bob"))
        assertFalse(graph.hasNode(" "))
        assertFalse(graph.hasEdge("alice", "alice"))
    }
}
