package com.opencontacts.androidecosystem.contacts

data class ContactRecord(
    val id: String,
    val displayName: String? = null,
    val firstName: String? = null,
    val lastName: String? = null,
    val email: String? = null,
    val phoneNumbers: List<String> = emptyList(),
    val company: String? = null,
    val jobTitle: String? = null,
    val address: String? = null,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val tags: Set<String> = emptySet(),
    val connectionIds: List<String> = emptyList(),
    val isFavorite: Boolean = false,
    val locationCategory: String? = null,
    val lastContactedAtEpochMillis: Long? = null,
    val interactionCount: Int = 0,
    val groups: List<String> = emptyList(),
    val photoUri: String? = null,
)
