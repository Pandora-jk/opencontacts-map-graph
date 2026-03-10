package com.openclaw.androidecosystem.contacts.contactssearch

import com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity
import com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph
import com.openclaw.androidecosystem.contacts.contactsgraph.GraphAlgorithm

enum class SuggestionReason {
    GRAPH_PROXIMITY,
    RECENT_ACTIVITY,
    STRONG_TIE
}

data class ContactSuggestion(
    val contact: ContactEntity,
    val score: Int,
    val reason: SuggestionReason
)

class ContactSuggestionEngine(
    private val graphAlgorithm: GraphAlgorithm = GraphAlgorithm()
) {
    fun suggestContacts(
        contacts: List<ContactEntity>,
        graph: ConnectionGraph,
        recentContactIds: Set<Long> = emptySet(),
        limit: Int = 5
    ): List<ContactSuggestion> {
        val graphSuggestions = recentContactIds
            .flatMap { graphAlgorithm.suggestConnections(it, graph, limit * 2) }
            .groupingBy { it }
            .eachCount()

        return contacts.map { contact ->
            val graphScore = (graphSuggestions[contact.id] ?: 0) * 20
            val recentBonus = if (contact.id in recentContactIds) 25 else 0
            val recencyBonus = when {
                contact.lastContacted == null -> 0
                System.currentTimeMillis() - contact.lastContacted <= DAY_MS * 7 -> 15
                else -> 5
            }
            val score = contact.connectionStrength + graphScore + recentBonus + recencyBonus
            ContactSuggestion(
                contact = contact,
                score = score,
                reason = when {
                    graphScore > 0 -> SuggestionReason.GRAPH_PROXIMITY
                    recentBonus > 0 || recencyBonus >= 15 -> SuggestionReason.RECENT_ACTIVITY
                    else -> SuggestionReason.STRONG_TIE
                }
            )
        }
            .sortedWith(
                compareByDescending<ContactSuggestion> { it.score }
                    .thenBy { it.contact.displayName.lowercase() }
            )
            .take(limit.coerceAtLeast(1))
    }

    private companion object {
        const val DAY_MS = 24L * 60L * 60L * 1000L
    }
}
