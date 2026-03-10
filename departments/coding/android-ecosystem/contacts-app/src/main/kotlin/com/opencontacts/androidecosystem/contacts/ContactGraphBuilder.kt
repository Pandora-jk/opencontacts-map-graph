package com.opencontacts.androidecosystem.contacts

class ContactGraphBuilder {
    fun buildGraph(contacts: List<ContactRecord>?): Map<String, Set<String>> {
        val validContacts = contacts.orEmpty()
            .mapNotNull { contact ->
                contact.id.trim().takeIf { it.isNotEmpty() }?.let { normalizedId -> normalizedId to contact }
            }
            .toMap(linkedMapOf())

        val graph = validContacts.keys.associateWith { linkedSetOf<String>() }.toMutableMap()
        for ((id, contact) in validContacts) {
            for (connectionId in contact.connectionIds) {
                val normalizedConnectionId = connectionId.trim()
                if (normalizedConnectionId.isEmpty() || normalizedConnectionId == id || normalizedConnectionId !in validContacts) {
                    continue
                }

                graph.getValue(id).add(normalizedConnectionId)
                graph.getValue(normalizedConnectionId).add(id)
            }
        }

        return graph.mapValues { (_, neighbors) -> neighbors.toSet() }
    }
}
