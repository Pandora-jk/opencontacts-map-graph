package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactSearchFilterTest {
    private val contactSearchFilter = ContactSearchFilter()

    private val contacts = listOf(
        ContactRecord(
            id = "1",
            displayName = "Ada Lovelace",
            email = "ada@example.com",
            company = "Analytical Engines",
            tags = setOf("mathematics"),
            isFavorite = true,
        ),
        ContactRecord(
            id = "2",
            displayName = "Grace Hopper",
            email = "grace@navy.mil",
            company = "US Navy",
            tags = setOf("compiler"),
            isFavorite = false,
        ),
        ContactRecord(
            id = "3",
            displayName = "Katherine Johnson",
            email = "kj@nasa.gov",
            company = "NASA",
            tags = setOf("orbital mechanics"),
            isFavorite = true,
        ),
    )

    @Test
    fun filter_matchesQueryAcrossSearchableFields_caseInsensitively() {
        assertEquals(listOf("1"), contactSearchFilter.filter(contacts, query = "analytical").map { it.id })
        assertEquals(listOf("2"), contactSearchFilter.filter(contacts, query = "NAVY").map { it.id })
        assertEquals(listOf("3"), contactSearchFilter.filter(contacts, query = "orbital").map { it.id })
        assertEquals(listOf("1"), contactSearchFilter.filter(contacts, query = "ada@example").map { it.id })
    }

    @Test
    fun filter_combinesFavoriteAndCompanyFilters() {
        val filtered = contactSearchFilter.filter(
            contacts = contacts,
            query = "nasa",
            favoriteOnly = true,
            company = "NASA",
        )

        assertEquals(listOf("3"), filtered.map { it.id })
    }

    @Test
    fun filter_handlesNullListsAndBlankQueries() {
        assertTrue(contactSearchFilter.filter(null, query = "ada").isEmpty())
        assertEquals(contacts, contactSearchFilter.filter(contacts, query = "   "))
        assertEquals(listOf("1", "3"), contactSearchFilter.filter(contacts, favoriteOnly = true).map { it.id })
    }
}
