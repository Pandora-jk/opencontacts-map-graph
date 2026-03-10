package com.openclaw.androidecosystem.contacts.contactssearch

import com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity
import com.openclaw.androidecosystem.contacts.contactsmap.ContactLocation
import com.openclaw.androidecosystem.contacts.contactsmap.GeoCoordinate
import com.openclaw.androidecosystem.contacts.contactsmap.LocationCategory

class ContactSearchFilter {
    fun filterContacts(
        contacts: List<ContactEntity>,
        query: String = "",
        minimumConnectionStrength: Int = 0,
        locations: List<ContactLocation> = emptyList(),
        anchor: GeoCoordinate? = null,
        maxDistanceKm: Double? = null,
        categories: Set<LocationCategory> = emptySet()
    ): List<ContactEntity> {
        val trimmedQuery = query.trim()
        val locationsByContact = locations.groupBy(ContactLocation::contactId)

        return contacts.filter { contact ->
            val matchesText = trimmedQuery.isBlank() || matchesQuery(contact, trimmedQuery)
            val matchesStrength = contact.connectionStrength >= minimumConnectionStrength
            val matchesLocation = matchesLocationFilter(
                contact = contact,
                contactLocations = locationsByContact[contact.id].orEmpty(),
                anchor = anchor,
                maxDistanceKm = maxDistanceKm,
                categories = categories
            )
            matchesText && matchesStrength && matchesLocation
        }.sortedWith(
            compareByDescending<ContactEntity> { it.connectionStrength }
                .thenBy { it.displayName.lowercase() }
        )
    }

    private fun matchesQuery(contact: ContactEntity, query: String): Boolean {
        return contact.displayName.contains(query, ignoreCase = true) ||
            contact.phone.orEmpty().contains(query.filter(Char::isDigit)) ||
            contact.email.orEmpty().contains(query, ignoreCase = true)
    }

    private fun matchesLocationFilter(
        contact: ContactEntity,
        contactLocations: List<ContactLocation>,
        anchor: GeoCoordinate?,
        maxDistanceKm: Double?,
        categories: Set<LocationCategory>
    ): Boolean {
        if (categories.isEmpty() && (anchor == null || maxDistanceKm == null)) {
            return true
        }

        if (contactLocations.isEmpty()) {
            return false
        }

        return contactLocations.any { location ->
            val matchesCategory = categories.isEmpty() || location.category in categories
            val matchesDistance = anchor == null || maxDistanceKm == null || location.isWithin(anchor, maxDistanceKm)
            matchesCategory && matchesDistance
        }
    }
}
