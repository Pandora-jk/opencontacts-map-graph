package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactGraphBuilderTest {
    private val graphBuilder = ContactGraphBuilder()

    @Test
    fun buildGraph_createsBidirectionalConnectionsAndDeduplicatesNeighbors() {
        val contacts = listOf(
            ContactRecord(id = "alice", connectionIds = listOf("bob", "carol", "bob")),
            ContactRecord(id = "bob", connectionIds = listOf("alice")),
            ContactRecord(id = "carol", connectionIds = listOf("alice")),
        )

        val graph = graphBuilder.buildGraph(contacts)

        assertEquals(setOf("bob", "carol"), graph["alice"])
        assertEquals(setOf("alice"), graph["bob"])
        assertEquals(setOf("alice"), graph["carol"])
    }

    @Test
    fun buildGraph_ignoresSelfReferencesUnknownContactsAndBlankIds() {
        val contacts = listOf(
            ContactRecord(id = "alice", connectionIds = listOf("alice", "missing", "bob")),
            ContactRecord(id = "bob", connectionIds = listOf("   ")),
            ContactRecord(id = "   ", connectionIds = listOf("alice")),
        )

        val graph = graphBuilder.buildGraph(contacts)

        assertEquals(mapOf("alice" to setOf("bob"), "bob" to setOf("alice")), graph)
    }

    @Test
    fun buildGraph_handlesNullAndEmptyInput() {
        assertEquals(emptyMap<String, Set<String>>(), graphBuilder.buildGraph(null))
        assertEquals(emptyMap<String, Set<String>>(), graphBuilder.buildGraph(emptyList()))
    }

    @Test
    fun buildGraph_preservesIsolatedNodes() {
        val graph = graphBuilder.buildGraph(
            listOf(
                contact(id = "alice"),
                contact(id = "bob"),
            )
        )

        assertEquals(setOf("alice", "bob"), graph.keys)
        assertEquals(emptySet<String>(), graph["alice"])
        assertEquals(emptySet<String>(), graph["bob"])
    }

    @Test
    fun buildGraph_usesLastContactWhenDuplicateIdsAppear() {
        val graph = graphBuilder.buildGraph(
            listOf(
                contact(id = "alice", connectionIds = listOf("bob")),
                contact(id = "alice", connectionIds = listOf("carol")),
                contact(id = "bob"),
                contact(id = "carol"),
            )
        )

        assertEquals(setOf("carol"), graph["alice"])
        assertEquals(emptySet<String>(), graph["bob"])
    }

    @Test
    fun buildConnectionGraph_createsConnectionGraphWrapper() {
        val graph = graphBuilder.buildConnectionGraph(
            listOf(
                contact(id = "alice", connectionIds = listOf("bob")),
                contact(id = "bob"),
            )
        )

        assertTrue(graph.hasEdge("alice", "bob"))
        assertEquals(2, graph.nodes().size)
    }

    @Test
    fun buildConnectionGraph_returnsEmptyGraphForEmptyInput() {
        val graph = graphBuilder.buildConnectionGraph(emptyList())

        assertTrue(graph.nodes().isEmpty())
        assertFalse(graph.hasNode("alice"))
    }
}
