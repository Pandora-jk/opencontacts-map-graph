package com.opencontacts.androidecosystem.contacts

import io.mockk.every
import io.mockk.mockk
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactSuggestionEngineTest {
    private val now = 1_700_000_000_000L
    private val nowProvider = mockk<() -> Long>()
    private val engine: ContactSuggestionEngine
    private val origin = ContactLocation("origin", 37.7749, -122.4194)

    init {
        every { nowProvider.invoke() } returns now
        engine = ContactSuggestionEngine(nowProvider)
    }

    @Test
    fun suggest_returnsEmptyForNullContacts() {
        assertTrue(engine.suggest(null).isEmpty())
    }

    @Test
    fun suggest_returnsEmptyForNonPositiveLimit() {
        assertTrue(engine.suggest(emptyList(), maxSuggestions = 0).isEmpty())
    }

    @Test
    fun suggest_ordersContactsByProximity() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "near", latitude = 37.7749, longitude = -122.4194),
                contact(id = "mid", latitude = 37.8044, longitude = -122.2711),
            ),
            origin = origin,
        )

        assertEquals(listOf("near", "mid"), suggestions.map { it.contactId })
    }

    @Test
    fun suggest_usesRecencyWeightingToBoostRecentContacts() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "stale-near", latitude = 37.7749, longitude = -122.4194, lastContactedAtEpochMillis = now - 45L * 24 * 60 * 60 * 1000),
                contact(id = "recent-farther", latitude = 37.8044, longitude = -122.2711, lastContactedAtEpochMillis = now),
            ),
            origin = origin,
        )

        assertEquals("recent-farther", suggestions.first().contactId)
    }

    @Test
    fun suggest_usesInteractionCountToBreakTies() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "low", latitude = 37.7749, longitude = -122.4194, interactionCount = 1),
                contact(id = "high", latitude = 37.7749, longitude = -122.4194, interactionCount = 5),
            ),
            origin = origin,
        )

        assertEquals("high", suggestions.first().contactId)
    }

    @Test
    fun suggest_limitsResultCount() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "1", latitude = 37.7749, longitude = -122.4194),
                contact(id = "2", latitude = 37.8044, longitude = -122.2711),
                contact(id = "3", latitude = 34.0522, longitude = -118.2437),
            ),
            origin = origin,
            maxSuggestions = 2,
        )

        assertEquals(2, suggestions.size)
    }

    @Test
    fun suggest_appliesCategoryFilterCaseInsensitively() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "1", latitude = 37.7749, longitude = -122.4194, locationCategory = "Work"),
                contact(id = "2", latitude = 37.7749, longitude = -122.4194, locationCategory = "Home"),
            ),
            origin = origin,
            category = " work ",
        )

        assertEquals(listOf("1"), suggestions.map { it.contactId })
    }

    @Test
    fun suggest_usesRecencyOnlyWhenOriginIsInvalid() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "recent", lastContactedAtEpochMillis = now),
                contact(id = "old", lastContactedAtEpochMillis = now - 60L * 24 * 60 * 60 * 1000),
            ),
            origin = ContactLocation("origin", null, null),
        )

        assertEquals(listOf("recent", "old"), suggestions.map { it.contactId })
    }

    @Test
    fun suggest_skipsContactsWithoutValidLocationWhenOriginIsValid() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "valid", latitude = 37.7749, longitude = -122.4194),
                contact(id = "invalid", latitude = null, longitude = -122.4194),
            ),
            origin = origin,
        )

        assertEquals(listOf("valid"), suggestions.map { it.contactId })
    }

    @Test
    fun suggest_deduplicatesByNormalizedContactIdKeepingHighestScore() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = " alice ", latitude = 37.7749, longitude = -122.4194),
                contact(id = "alice", latitude = 34.0522, longitude = -118.2437),
            ),
            origin = origin,
        )

        assertEquals(listOf("alice"), suggestions.map { it.contactId })
    }

    @Test
    fun suggest_appliesFavoriteBoost() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "favorite", latitude = 37.7749, longitude = -122.4194, isFavorite = true),
                contact(id = "regular", latitude = 37.7749, longitude = -122.4194, isFavorite = false),
            ),
            origin = origin,
        )

        assertEquals("favorite", suggestions.first().contactId)
    }

    @Test
    fun suggest_setsReasonToNearbyAndRecentWhenBothSignalsExist() {
        val suggestion = engine.suggest(
            contacts = listOf(
                contact(id = "1", latitude = 37.7749, longitude = -122.4194, lastContactedAtEpochMillis = now)
            ),
            origin = origin,
        ).single()

        assertEquals("Nearby and recent", suggestion.reason)
    }

    @Test
    fun suggest_breaksScoreTiesAlphabeticallyByTitle() {
        val suggestions = engine.suggest(
            contacts = listOf(
                contact(id = "2", displayName = "Bravo", latitude = 37.7749, longitude = -122.4194),
                contact(id = "1", displayName = "Alpha", latitude = 37.7749, longitude = -122.4194),
            ),
            origin = origin,
        )

        assertEquals(listOf("Alpha", "Bravo"), suggestions.map { it.title })
    }
}
