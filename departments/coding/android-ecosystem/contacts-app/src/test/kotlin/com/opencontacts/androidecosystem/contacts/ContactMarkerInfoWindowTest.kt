package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactMarkerInfoWindowTest {
    private val infoWindow = ContactMarkerInfoWindow()

    @Test
    fun contentFor_usesMarkerTitleAndSubtitle() {
        val content = infoWindow.contentFor(
            ContactMapMarker("1", "Ada", "ada@example.com", 1.0, 2.0, "work", 3.4, false, 2)
        )

        assertEquals("Ada", content.title)
        assertEquals("ada@example.com", content.subtitle)
    }

    @Test
    fun contentFor_formatsMetaWithCategoryAndStrength() {
        val content = infoWindow.contentFor(
            ContactMapMarker("1", "Ada", "ada@example.com", 1.0, 2.0, "work", 3.4, false, 2)
        )

        assertEquals("work • strength 2", content.meta)
    }

    @Test
    fun contentFor_formatsDistanceWithOneDecimalPlace() {
        val content = infoWindow.contentFor(
            ContactMapMarker("1", "Ada", "ada@example.com", 1.0, 2.0, "work", 3.44, false, 2)
        )

        assertEquals("3.4 km away", content.distance)
    }

    @Test
    fun contentFor_usesFallbacksForBlankSubtitleAndMissingDistance() {
        val content = infoWindow.contentFor(
            ContactMapMarker("1", "Ada", "", 1.0, 2.0, null, null, false, 0)
        )

        assertEquals("No phone or email on file", content.subtitle)
        assertEquals("uncategorized • strength 0", content.meta)
        assertEquals("Distance unavailable", content.distance)
    }

    @Test
    fun contentFor_includesMarkerTitleInContentDescription() {
        val content = infoWindow.contentFor(
            ContactMapMarker("1", "Ada", "ada@example.com", 1.0, 2.0, "work", 3.4, false, 2)
        )

        assertTrue(content.contentDescription.contains("Ada"))
    }
}
