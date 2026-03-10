package com.opencontacts.androidecosystem.contacts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactLocationTest {
    @Test
    fun isValid_acceptsBoundaryCoordinates() {
        assertTrue(ContactLocation("1", 90.0, 180.0).isValid())
        assertTrue(ContactLocation("2", -90.0, -180.0).isValid())
    }

    @Test
    fun isValid_rejectsLatitudeAboveRange() {
        assertFalse(ContactLocation("1", 90.1, 0.0).isValid())
    }

    @Test
    fun isValid_rejectsLatitudeBelowRange() {
        assertFalse(ContactLocation("1", -90.1, 0.0).isValid())
    }

    @Test
    fun isValid_rejectsLongitudeAboveRange() {
        assertFalse(ContactLocation("1", 0.0, 180.1).isValid())
    }

    @Test
    fun isValid_rejectsLongitudeBelowRange() {
        assertFalse(ContactLocation("1", 0.0, -180.1).isValid())
    }

    @Test
    fun isValid_rejectsNullLatitude() {
        assertFalse(ContactLocation("1", null, 0.0).isValid())
    }

    @Test
    fun isValid_rejectsNullLongitude() {
        assertFalse(ContactLocation("1", 0.0, null).isValid())
    }

    @Test
    fun normalizedCategory_trimsAndLowercases() {
        assertEquals("work", ContactLocation("1", 0.0, 0.0, " Work ").normalizedCategory())
    }

    @Test
    fun distanceTo_returnsZeroForSamePoint() {
        val location = ContactLocation("1", 37.7749, -122.4194)

        assertEquals(0.0, location.distanceTo(location), 0.0)
    }

    @Test
    fun distanceTo_returnsExpectedDistanceForKnownCities() {
        val sanFrancisco = ContactLocation("sf", 37.7749, -122.4194)
        val losAngeles = ContactLocation("la", 34.0522, -118.2437)

        assertEquals(559.0, sanFrancisco.distanceTo(losAngeles)!!, 10.0)
    }

    @Test
    fun distanceTo_returnsNullWhenEitherLocationIsInvalid() {
        val valid = ContactLocation("1", 0.0, 0.0)
        val invalid = ContactLocation("2", null, 10.0)

        assertNull(valid.distanceTo(invalid))
        assertNull(invalid.distanceTo(valid))
    }

    @Test
    fun fromContact_usesLocationCategoryOrFirstTag() {
        assertEquals(
            "home",
            ContactLocation.fromContact(contact(id = "1", latitude = 1.0, longitude = 2.0, locationCategory = " Home "))?.normalizedCategory()
        )
        assertEquals(
            "friend",
            ContactLocation.fromContact(contact(id = "2", latitude = 1.0, longitude = 2.0, tags = setOf("Friend")))?.normalizedCategory()
        )
    }
}
