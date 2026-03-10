package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class GraphVisualizationViewTest {
    private val view = GraphVisualizationView()

    @Test
    fun render_returnsEmptyStateForNullGraph() {
        val state = view.render(null, width = 100, height = 100)

        assertTrue(state.nodes.isEmpty())
        assertTrue(state.edges.isEmpty())
    }

    @Test
    fun render_returnsEmptyStateForNonPositiveBounds() {
        val state = view.render(graphOf(nodes = listOf("alice")), width = 0, height = 100)

        assertTrue(state.nodes.isEmpty())
    }

    @Test
    fun render_positionsSingleNodeAtCenter() {
        val state = view.render(graphOf(nodes = listOf("alice")), width = 200, height = 100)
        val node = state.nodes.single()

        assertEquals(100f, node.x, 0.01f)
        assertEquals(50f, node.y, 0.01f)
    }

    @Test
    fun render_keepsAllNodesWithinBounds() {
        val state = view.render(
            graphOf(edges = arrayOf("alice" to "bob", "bob" to "carol", "carol" to "dave")),
            width = 200,
            height = 150,
        )

        assertEquals(4, state.nodes.size)
        assertTrue(state.nodes.all { it.x in 0f..200f && it.y in 0f..150f })
    }

    @Test
    fun render_deduplicatesUndirectedEdges() {
        val graph = ConnectionGraph().apply {
            addEdge("alice", "bob")
            addEdge("bob", "alice")
        }

        val state = view.render(graph, width = 100, height = 100)

        assertEquals(listOf(GraphRenderEdge("alice", "bob")), state.edges)
    }

    @Test
    fun render_preservesDisconnectedNodesWithoutEdges() {
        val state = view.render(graphOf(nodes = listOf("alice", "bob")), width = 100, height = 100)

        assertEquals(2, state.nodes.size)
        assertTrue(state.edges.isEmpty())
    }
}
