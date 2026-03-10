package com.opencontacts.androidecosystem.contacts

internal fun contact(
    id: String,
    displayName: String? = "Contact $id",
    email: String? = null,
    company: String? = null,
    latitude: Double? = null,
    longitude: Double? = null,
    tags: Set<String> = emptySet(),
    connectionIds: List<String> = emptyList(),
    isFavorite: Boolean = false,
    phoneNumbers: List<String> = emptyList(),
    locationCategory: String? = null,
    lastContactedAtEpochMillis: Long? = null,
    interactionCount: Int = 0,
): ContactRecord {
    return ContactRecord(
        id = id,
        displayName = displayName,
        email = email,
        company = company,
        latitude = latitude,
        longitude = longitude,
        tags = tags,
        connectionIds = connectionIds,
        isFavorite = isFavorite,
        phoneNumbers = phoneNumbers,
        locationCategory = locationCategory,
        lastContactedAtEpochMillis = lastContactedAtEpochMillis,
        interactionCount = interactionCount,
    )
}

internal fun graphOf(
    nodes: List<String> = emptyList(),
    edges: Array<out Pair<String, String>> = emptyArray(),
): ConnectionGraph {
    return ConnectionGraph().apply {
        nodes.forEach(::addNode)
        edges.forEach { (first, second) -> addEdge(first, second) }
    }
}
