package com.opencontacts.androidecosystem.contacts

class ContactSuggestionEngine(
    private val nowProvider: () -> Long = { System.currentTimeMillis() },
) {
    fun suggest(
        contacts: List<ContactRecord>?,
        origin: ContactLocation? = null,
        maxSuggestions: Int = 5,
        category: String? = null,
    ): List<ContactSuggestion> {
        if (maxSuggestions <= 0) {
            return emptyList()
        }

        val normalizedCategory = category?.trim()?.lowercase().orEmpty()
        return contacts.orEmpty()
            .mapNotNull { contact -> toSuggestion(contact, origin, normalizedCategory) }
            .groupBy { it.contactId }
            .values
            .map { suggestions -> suggestions.maxBy { it.score } }
            .sortedWith(
                compareByDescending<ContactSuggestion> { it.score }
                    .thenBy { it.title.lowercase() }
                    .thenBy { it.contactId }
            )
            .take(maxSuggestions)
    }

    private fun toSuggestion(
        contact: ContactRecord,
        origin: ContactLocation?,
        normalizedCategory: String,
    ): ContactSuggestion? {
        val normalizedId = contact.id.trim().takeIf(String::isNotEmpty) ?: return null
        val location = ContactLocation.fromContact(contact)
        val category = location?.normalizedCategory()
        if (normalizedCategory.isNotEmpty() && category != normalizedCategory) {
            return null
        }

        val hasValidOrigin = origin?.isValid() == true
        val distance = if (hasValidOrigin) origin?.distanceTo(location) else null
        if (hasValidOrigin && distance == null) {
            return null
        }

        val title = contact.displayName?.trim().takeUnless { it.isNullOrEmpty() }
            ?: contact.email?.trim().takeUnless { it.isNullOrEmpty() }
            ?: contact.phoneNumbers.firstOrNull { it.trim().isNotEmpty() }?.trim()
            ?: "Unknown contact"

        val score = proximityScore(distance) +
            recencyScore(contact.lastContactedAtEpochMillis) +
            minOf(20, contact.interactionCount * 2) +
            if (contact.isFavorite) 5 else 0

        val reason = when {
            distance != null && recencyScore(contact.lastContactedAtEpochMillis) > 0 -> "Nearby and recent"
            distance != null -> "Nearby"
            recencyScore(contact.lastContactedAtEpochMillis) > 0 -> "Recent"
            else -> "Relevant"
        }

        return ContactSuggestion(
            contactId = normalizedId,
            title = title,
            score = score,
            distanceKm = distance,
            reason = reason,
        )
    }

    private fun proximityScore(distanceKm: Double?): Int = when {
        distanceKm == null -> 0
        distanceKm <= 5.0 -> 60
        distanceKm <= 25.0 -> 40
        distanceKm <= 100.0 -> 20
        else -> 0
    }

    private fun recencyScore(lastContactedAtEpochMillis: Long?): Int {
        val lastContactedAt = lastContactedAtEpochMillis ?: return 0
        val elapsedMillis = (nowProvider() - lastContactedAt).coerceAtLeast(0)
        val elapsedDays = elapsedMillis / DAY_IN_MILLIS
        return when {
            elapsedDays <= 1 -> 40
            elapsedDays <= 7 -> 25
            elapsedDays <= 30 -> 10
            else -> 0
        }
    }

    private companion object {
        const val DAY_IN_MILLIS = 24L * 60L * 60L * 1000L
    }
}
