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
)

data class MapMarker(
    val contactId: String,
    val title: String,
    val latitude: Double,
    val longitude: Double,
)
