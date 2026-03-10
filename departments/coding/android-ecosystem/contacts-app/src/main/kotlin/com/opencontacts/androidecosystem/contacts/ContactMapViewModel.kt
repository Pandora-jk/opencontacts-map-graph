package com.opencontacts.androidecosystem.contacts

class ContactMapViewModel {
    fun toMarkers(
        contacts: List<ContactRecord>?,
        origin: ContactLocation? = null,
    ): List<ContactMapMarker> {
        return contacts.orEmpty().mapNotNull { contact ->
            val normalizedId = contact.id.trim().takeIf(String::isNotEmpty) ?: return@mapNotNull null
            val location = ContactLocation.fromContact(contact) ?: return@mapNotNull null
            if (!location.isValid()) {
                return@mapNotNull null
            }

            val title = contact.displayName?.trim().takeUnless { it.isNullOrEmpty() }
                ?: contact.email?.trim().takeUnless { it.isNullOrEmpty() }
                ?: contact.phoneNumbers.firstOrNull { it.trim().isNotEmpty() }?.trim()
                ?: "Unknown contact"
            val subtitle = contact.company?.trim().takeUnless { it.isNullOrEmpty() }
                ?: contact.email?.trim().takeUnless { it.isNullOrEmpty() }
                ?: contact.phoneNumbers.firstOrNull { it.trim().isNotEmpty() }?.trim()
                ?: "No phone or email on file"

            ContactMapMarker(
                contactId = normalizedId,
                title = title,
                subtitle = subtitle,
                latitude = location.latitude!!,
                longitude = location.longitude!!,
                category = location.normalizedCategory(),
                distanceKm = origin?.distanceTo(location),
                isFavorite = contact.isFavorite,
                connectionStrength = contact.connectionIds.map(String::trim).filter(String::isNotEmpty).distinct().size,
            )
        }
    }

    fun filterMarkers(
        markers: List<ContactMapMarker>?,
        maxDistanceKm: Double? = null,
        category: String? = null,
        favoriteOnly: Boolean = false,
    ): List<ContactMapMarker> {
        val normalizedCategory = category?.trim()?.lowercase().orEmpty()
        return markers.orEmpty().filter { marker ->
            val matchesDistance = maxDistanceKm == null || (marker.distanceKm != null && marker.distanceKm <= maxDistanceKm)
            val matchesCategory = normalizedCategory.isEmpty() || marker.category == normalizedCategory
            val matchesFavorite = !favoriteOnly || marker.isFavorite
            matchesDistance && matchesCategory && matchesFavorite
        }
    }

    fun updateState(
        markers: List<ContactMapMarker>?,
        maxDistanceKm: Double? = null,
        category: String? = null,
        favoriteOnly: Boolean = false,
    ): ContactMapUiState {
        val filteredMarkers = filterMarkers(
            markers = markers,
            maxDistanceKm = maxDistanceKm,
            category = category,
            favoriteOnly = favoriteOnly,
        )
        val count = filteredMarkers.size
        val statusMessage = if (count == 0) {
            "No contacts match the current filters."
        } else {
            "$count contacts in view"
        }
        return ContactMapUiState(
            markers = filteredMarkers,
            visibleCount = count,
            activeCategory = category?.trim()?.lowercase()?.takeIf(String::isNotEmpty),
            maxDistanceKm = maxDistanceKm,
            favoriteOnly = favoriteOnly,
            statusMessage = statusMessage,
        )
    }
}
