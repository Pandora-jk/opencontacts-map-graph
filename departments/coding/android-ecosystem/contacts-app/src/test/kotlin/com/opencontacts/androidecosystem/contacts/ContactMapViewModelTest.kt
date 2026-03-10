package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactMapViewModelTest {
    private val viewModel = ContactMapViewModel()
    private val origin = ContactLocation("origin", 37.7749, -122.4194, "home")

    @Test
    fun toMarkers_createsMarkerForValidContact() {
        val marker = viewModel.toMarkers(
            listOf(
                contact(
                    id = "1",
                    displayName = "Ada Lovelace",
                    company = "Analytical Engines",
                    latitude = 37.7749,
                    longitude = -122.4194,
                    locationCategory = "Work",
                )
            ),
            origin = origin,
        ).single()

        assertEquals("Ada Lovelace", marker.title)
        assertEquals("Analytical Engines", marker.subtitle)
        assertEquals("work", marker.category)
        assertEquals(0.0, marker.distanceKm!!, 0.0)
    }

    @Test
    fun toMarkers_usesEmailWhenDisplayNameIsBlank() {
        val marker = viewModel.toMarkers(
            listOf(contact(id = "1", displayName = "  ", email = "ada@example.com", latitude = 1.0, longitude = 2.0))
        ).single()

        assertEquals("ada@example.com", marker.title)
    }

    @Test
    fun toMarkers_usesPhoneWhenDisplayNameAndEmailMissing() {
        val marker = viewModel.toMarkers(
            listOf(contact(id = "1", displayName = null, email = null, phoneNumbers = listOf("555-0100"), latitude = 1.0, longitude = 2.0))
        ).single()

        assertEquals("555-0100", marker.title)
    }

    @Test
    fun toMarkers_fallsBackToUnknownContactTitle() {
        val marker = viewModel.toMarkers(
            listOf(contact(id = "1", displayName = null, email = null, phoneNumbers = emptyList(), latitude = 1.0, longitude = 2.0))
        ).single()

        assertEquals("Unknown contact", marker.title)
    }

    @Test
    fun toMarkers_skipsContactsWithBlankIds() {
        assertTrue(
            viewModel.toMarkers(listOf(contact(id = " ", latitude = 1.0, longitude = 2.0))).isEmpty()
        )
    }

    @Test
    fun toMarkers_skipsContactsWithInvalidCoordinates() {
        val markers = viewModel.toMarkers(
            listOf(
                contact(id = "1", latitude = 91.0, longitude = 0.0),
                contact(id = "2", latitude = 0.0, longitude = 181.0),
            )
        )

        assertTrue(markers.isEmpty())
    }

    @Test
    fun toMarkers_usesFirstTagAsCategoryWhenLocationCategoryMissing() {
        val marker = viewModel.toMarkers(
            listOf(contact(id = "1", latitude = 1.0, longitude = 2.0, tags = setOf("Friends")))
        ).single()

        assertEquals("friends", marker.category)
    }

    @Test
    fun toMarkers_leavesDistanceNullWhenOriginMissing() {
        val marker = viewModel.toMarkers(
            listOf(contact(id = "1", latitude = 1.0, longitude = 2.0))
        ).single()

        assertNull(marker.distanceKm)
    }

    @Test
    fun toMarkers_usesDistinctConnectionCountAsStrength() {
        val marker = viewModel.toMarkers(
            listOf(contact(id = "1", latitude = 1.0, longitude = 2.0, connectionIds = listOf("a", "a", "b", " ")))
        ).single()

        assertEquals(2, marker.connectionStrength)
    }

    @Test
    fun filterMarkers_filtersByDistance() {
        val markers = viewModel.toMarkers(
            listOf(
                contact(id = "near", latitude = 37.7749, longitude = -122.4194),
                contact(id = "far", latitude = 34.0522, longitude = -118.2437),
            ),
            origin = origin,
        )

        assertEquals(listOf("near"), viewModel.filterMarkers(markers, maxDistanceKm = 10.0).map { it.contactId })
    }

    @Test
    fun filterMarkers_filtersByCategoryCaseInsensitively() {
        val markers = viewModel.toMarkers(
            listOf(
                contact(id = "1", latitude = 1.0, longitude = 2.0, locationCategory = "Work"),
                contact(id = "2", latitude = 1.0, longitude = 2.0, locationCategory = "Home"),
            )
        )

        assertEquals(listOf("1"), viewModel.filterMarkers(markers, category = " work ").map { it.contactId })
    }

    @Test
    fun filterMarkers_filtersFavoritesOnly() {
        val markers = viewModel.toMarkers(
            listOf(
                contact(id = "1", latitude = 1.0, longitude = 2.0, isFavorite = true),
                contact(id = "2", latitude = 1.0, longitude = 2.0, isFavorite = false),
            )
        )

        assertEquals(listOf("1"), viewModel.filterMarkers(markers, favoriteOnly = true).map { it.contactId })
    }

    @Test
    fun filterMarkers_handlesNullMarkers() {
        assertTrue(viewModel.filterMarkers(null).isEmpty())
    }

    @Test
    fun updateState_returnsEmptyStateMessageWhenNoMarkersMatch() {
        val markers = viewModel.toMarkers(
            listOf(contact(id = "1", latitude = 1.0, longitude = 2.0, locationCategory = "home"))
        )

        val state = viewModel.updateState(markers, category = "work")

        assertEquals(0, state.visibleCount)
        assertEquals("No contacts match the current filters.", state.statusMessage)
    }

    @Test
    fun updateState_tracksFiltersAndVisibleCount() {
        val markers = viewModel.toMarkers(
            listOf(
                contact(id = "1", latitude = 1.0, longitude = 2.0, locationCategory = "work", isFavorite = true),
                contact(id = "2", latitude = 1.0, longitude = 2.0, locationCategory = "work", isFavorite = false),
            )
        )

        val state = viewModel.updateState(markers, category = "WORK", favoriteOnly = true)

        assertEquals(1, state.visibleCount)
        assertEquals("work", state.activeCategory)
        assertTrue(state.favoriteOnly)
        assertEquals("1 contacts in view", state.statusMessage)
    }
}
