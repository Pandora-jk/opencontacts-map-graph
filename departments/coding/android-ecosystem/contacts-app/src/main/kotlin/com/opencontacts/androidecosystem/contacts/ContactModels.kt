package com.opencontacts.androidecosystem.contacts

data class ContactRecord(
    val id: String,
    val displayName: String? = null,
    val email: String? = null,
    val company: String? = null,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val tags: Set<String> = emptySet(),
    val connectionIds: List<String> = emptyList(),
    val isFavorite: Boolean = false,
    val phoneNumbers: List<String> = emptyList(),
    val locationCategory: String? = null,
    val lastContactedAtEpochMillis: Long? = null,
    val interactionCount: Int = 0,
    val groups: List<String> = emptyList(),
)

data class MapMarker(
    val contactId: String,
    val title: String,
    val latitude: Double,
    val longitude: Double,
)

data class ContactMapMarker(
    val contactId: String,
    val title: String,
    val subtitle: String,
    val latitude: Double,
    val longitude: Double,
    val category: String?,
    val distanceKm: Double?,
    val isFavorite: Boolean,
    val connectionStrength: Int,
)

data class ContactMapUiState(
    val markers: List<ContactMapMarker> = emptyList(),
    val visibleCount: Int = 0,
    val activeCategory: String? = null,
    val maxDistanceKm: Double? = null,
    val favoriteOnly: Boolean = false,
    val statusMessage: String = "0 contacts in view",
)

data class ContactSuggestion(
    val contactId: String,
    val title: String,
    val score: Int,
    val distanceKm: Double?,
    val reason: String,
)

data class ContactListItemModel(
    val title: String,
    val subtitle: String,
    val contentDescription: String,
    val isFavorite: Boolean,
)

data class MarkerInfoContent(
    val title: String,
    val subtitle: String,
    val meta: String,
    val distance: String,
    val contentDescription: String,
)

data class GraphRenderNode(
    val id: String,
    val x: Float,
    val y: Float,
)

data class GraphRenderEdge(
    val startId: String,
    val endId: String,
)

data class GraphRenderState(
    val nodes: List<GraphRenderNode>,
    val edges: List<GraphRenderEdge>,
    val width: Int,
    val height: Int,
)
