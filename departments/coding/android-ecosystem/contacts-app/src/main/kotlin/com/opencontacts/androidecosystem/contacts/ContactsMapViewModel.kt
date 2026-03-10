package com.opencontacts.androidecosystem.contacts

class ContactsMapViewModel {
    fun toMarkers(contacts: List<ContactRecord>?): List<MapMarker> {
        return contacts.orEmpty().mapNotNull { contact ->
            val normalizedId = contact.id.trim().takeIf { it.isNotEmpty() } ?: return@mapNotNull null
            val latitude = contact.latitude.takeIf { it != null && it in -90.0..90.0 } ?: return@mapNotNull null
            val longitude = contact.longitude.takeIf { it != null && it in -180.0..180.0 } ?: return@mapNotNull null
            val title = contact.displayName?.trim().takeUnless { it.isNullOrEmpty() }
                ?: contact.email?.trim().takeUnless { it.isNullOrEmpty() }
                ?: "Unknown contact"

            MapMarker(
                contactId = normalizedId,
                title = title,
                latitude = latitude,
                longitude = longitude,
            )
        }
    }
}
