package com.opencontacts.androidecosystem.contacts

/**
 * Mutable data class for contact records.
 * Fields are mutable to allow efficient batch loading from ContactsContract.
 */
class ContactRecord(
    val id: String,
    val displayName: String? = null,
    var firstName: String? = null,
    var lastName: String? = null,
    var email: String? = null,
    var phoneNumbers: MutableList<String> = mutableListOf(),
    var company: String? = null,
    var jobTitle: String? = null,
    var address: String? = null,
    val latitude: Double? = null,
    val longitude: Double? = null,
    val tags: Set<String> = emptySet(),
    val connectionIds: List<String> = emptyList(),
    val isFavorite: Boolean = false,
    val locationCategory: String? = null,
    val lastContactedAtEpochMillis: Long? = null,
    val interactionCount: Int = 0,
    var groups: List<String> = emptyList(),
    val photoUri: String? = null,
)
