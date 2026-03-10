package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactsMapViewModelTest {
    private val viewModel = ContactsMapViewModel()

    @Test
    fun toMarkers_convertsValidContactsToMarkers() {
        val contacts = listOf(
            ContactRecord(
                id = " contact-1 ",
                displayName = "Ada Lovelace",
                email = "ada@example.com",
                latitude = 37.7749,
                longitude = -122.4194,
            ),
            ContactRecord(
                id = "contact-2",
                displayName = "   ",
                email = "grace@example.com",
                latitude = 47.6062,
                longitude = -122.3321,
            ),
        )

        val markers = viewModel.toMarkers(contacts)

        assertEquals(
            listOf(
                MapMarker("contact-1", "Ada Lovelace", 37.7749, -122.4194),
                MapMarker("contact-2", "grace@example.com", 47.6062, -122.3321),
            ),
            markers,
        )
    }

    @Test
    fun toMarkers_filtersContactsWithMissingOrInvalidCoordinates() {
        val contacts = listOf(
            ContactRecord(id = "valid", displayName = "Valid", latitude = 10.0, longitude = 20.0),
            ContactRecord(id = "missing-lat", displayName = "Missing Lat", latitude = null, longitude = 20.0),
            ContactRecord(id = "bad-lon", displayName = "Bad Lon", latitude = 10.0, longitude = 181.0),
            ContactRecord(id = "   ", displayName = "Blank Id", latitude = 10.0, longitude = 20.0),
        )

        val markers = viewModel.toMarkers(contacts)

        assertEquals(1, markers.size)
        assertEquals("valid", markers.single().contactId)
    }

    @Test
    fun toMarkers_handlesNullOrEmptyInput_andUsesUnknownTitleFallback() {
        assertTrue(viewModel.toMarkers(null).isEmpty())
        assertTrue(viewModel.toMarkers(emptyList()).isEmpty())

        val marker = viewModel.toMarkers(
            listOf(ContactRecord(id = "contact-3", latitude = 1.0, longitude = 2.0))
        ).single()

        assertEquals(MapMarker("contact-3", "Unknown contact", 1.0, 2.0), marker)
    }
}
