package com.opencontacts.androidecosystem.contacts

class ContactSearchFilter {
    fun filter(
        contacts: List<ContactRecord>?,
        query: String? = null,
        favoriteOnly: Boolean = false,
        company: String? = null,
    ): List<ContactRecord> {
        val normalizedQuery = query?.trim()?.lowercase().orEmpty()
        val normalizedCompany = company?.trim()?.lowercase().orEmpty()

        return contacts.orEmpty().filter { contact ->
            val matchesFavorite = !favoriteOnly || contact.isFavorite
            val matchesCompany = normalizedCompany.isEmpty() ||
                contact.company?.trim()?.lowercase() == normalizedCompany
            val matchesQuery = normalizedQuery.isEmpty() || contact.matchesQuery(normalizedQuery)
            matchesFavorite && matchesCompany && matchesQuery
        }
    }

    private fun ContactRecord.matchesQuery(query: String): Boolean {
        val normalizedDigits = query.filter(Char::isDigit)

        return sequenceOf(displayName, email, company)
            .filterNotNull()
            .map { it.trim().lowercase() }
            .any { it.contains(query) } ||
            tags.any { it.trim().lowercase().contains(query) } ||
            (
                normalizedDigits.isNotEmpty() &&
                    phoneNumbers.any { phone ->
                        phone.filter(Char::isDigit).contains(normalizedDigits)
                    }
                )
    }
}
