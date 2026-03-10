package com.openclaw.androidecosystem.contacts.contactsgraph

import com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity

data class ConnectionNode(
    val contact: ContactEntity
)

data class ConnectionEdge(
    val fromContactId: Long,
    val toContactId: Long,
    val callCount: Int = 0,
    val smsCount: Int = 0,
    val emailCount: Int = 0,
    val lastInteraction: Long? = null
) {
    init {
        require(fromContactId != toContactId) { "Connection edges must join distinct contacts." }
    }

    fun normalized(): ConnectionEdge {
        return if (fromContactId <= toContactId) {
            this
        } else {
            copy(fromContactId = toContactId, toContactId = fromContactId)
        }
    }

    fun combine(other: ConnectionEdge): ConnectionEdge {
        val first = normalized()
        val second = other.normalized()
        require(first.fromContactId == second.fromContactId && first.toContactId == second.toContactId)
        return first.copy(
            callCount = first.callCount + second.callCount,
            smsCount = first.smsCount + second.smsCount,
            emailCount = first.emailCount + second.emailCount,
            lastInteraction = maxOf(first.lastInteraction ?: 0L, second.lastInteraction ?: 0L).takeIf {
                it > 0L
            }
        )
    }
}

data class ConnectionGraph(
    val nodes: Map<Long, ConnectionNode>,
    val edges: List<ConnectionEdge>
) {
    fun neighborsOf(contactId: Long): Set<Long> {
        return edges.flatMap { edge ->
            when (contactId) {
                edge.fromContactId -> listOf(edge.toContactId)
                edge.toContactId -> listOf(edge.fromContactId)
                else -> emptyList()
            }
        }.toSet()
    }

    fun edgeBetween(firstContactId: Long, secondContactId: Long): ConnectionEdge? {
        val low = minOf(firstContactId, secondContactId)
        val high = maxOf(firstContactId, secondContactId)
        return edges.firstOrNull { it.normalized().fromContactId == low && it.normalized().toContactId == high }
    }

    fun degreeOf(contactId: Long): Int = neighborsOf(contactId).size

    fun contains(contactId: Long): Boolean = nodes.containsKey(contactId)
}
