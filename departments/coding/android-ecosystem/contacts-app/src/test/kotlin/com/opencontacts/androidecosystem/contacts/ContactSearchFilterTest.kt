package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactSearchFilterTest {
    private val filter = ContactSearchFilter()

    private val contacts = listOf(
        contact(
            id = "1",
            displayName = "Ada Lovelace",
            email = "ada@example.com",
            company = "Analytical Engines",
            tags = setOf("Mathematics"),
            phoneNumbers = listOf("+1 (415) 555-0100"),
            isFavorite = true,
        ),
        contact(
            id = "2",
            displayName = "Grace Hopper",
            email = "grace@navy.mil",
            company = "US Navy",
            tags = setOf("Compiler"),
            phoneNumbers = listOf("415-555-0200"),
        ),
        contact(
            id = "3",
            displayName = "Katherine Johnson",
            email = "kj@nasa.gov",
            company = "NASA",
            tags = setOf("Orbital Mechanics"),
            phoneNumbers = listOf("202 555 0300"),
            isFavorite = true,
        ),
        contact(
            id = "4",
            displayName = null,
            email = null,
            company = null,
            tags = emptySet(),
            phoneNumbers = emptyList(),
        ),
    )

    @Test
    fun filter_returnsEmptyListForNullContacts() {
        assertTrue(filter.filter(null, query = "ada").isEmpty())
    }

    @Test
    fun filter_returnsOriginalContactsForNullQueryAndNoFilters() {
        val result = filter.filter(contacts, query = null)

        assertEquals(contacts, result)
    }

    @Test
    fun filter_matchesDisplayNameCaseInsensitively() {
        assertEquals(listOf("1"), filter.filter(contacts, query = "lovelace").map { it.id })
        assertEquals(listOf("2"), filter.filter(contacts, query = "GRACE").map { it.id })
    }

    @Test
    fun filter_matchesEmailCaseInsensitively() {
        assertEquals(listOf("3"), filter.filter(contacts, query = "NASA.GOV").map { it.id })
    }

    @Test
    fun filter_matchesCompanyCaseInsensitively() {
        assertEquals(listOf("1"), filter.filter(contacts, query = "analytical").map { it.id })
    }

    @Test
    fun filter_matchesTagsCaseInsensitively() {
        assertEquals(listOf("2"), filter.filter(contacts, query = "compiler").map { it.id })
    }

    @Test
    fun filter_matchesPhoneNumbersUsingDigitNormalization() {
        assertEquals(listOf("1"), filter.filter(contacts, query = "4155550100").map { it.id })
        assertEquals(listOf("3"), filter.filter(contacts, query = "555-0300").map { it.id })
    }

    @Test
    fun filter_returnsEmptyWhenQueryDoesNotMatchAnyField() {
        assertTrue(filter.filter(contacts, query = "not-found").isEmpty())
    }

    @Test
    fun filter_ignoresBlankQuery() {
        assertEquals(contacts, filter.filter(contacts, query = "   "))
    }

    @Test
    fun filter_filtersFavoritesOnly() {
        assertEquals(listOf("1", "3"), filter.filter(contacts, favoriteOnly = true).map { it.id })
    }

    @Test
    fun filter_filtersByCompanyWithTrimmedCaseInsensitiveValue() {
        assertEquals(listOf("3"), filter.filter(contacts, company = " nasa ").map { it.id })
    }

    @Test
    fun filter_ignoresBlankCompanyFilter() {
        assertEquals(contacts, filter.filter(contacts, company = "   "))
    }

    @Test
    fun filter_combinesQueryFavoriteAndCompanyFilters() {
        val result = filter.filter(
            contacts = contacts,
            query = "nasa",
            favoriteOnly = true,
            company = "NASA",
        )

        assertEquals(listOf("3"), result.map { it.id })
    }

    @Test
    fun filter_handlesContactsWithNullFieldsWithoutCrashing() {
        assertEquals(listOf("4"), filter.filter(listOf(contacts.last()), query = "   ").map { it.id })
        assertTrue(filter.filter(listOf(contacts.last()), query = "ada").isEmpty())
    }

    @Test
    fun filter_preservesDuplicateContactsInResults() {
        val duplicateList = contacts + contacts.first()

        val result = filter.filter(duplicateList, query = "ada")

        assertEquals(listOf("1", "1"), result.map { it.id })
    }
}
