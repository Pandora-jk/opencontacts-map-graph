package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
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
}
