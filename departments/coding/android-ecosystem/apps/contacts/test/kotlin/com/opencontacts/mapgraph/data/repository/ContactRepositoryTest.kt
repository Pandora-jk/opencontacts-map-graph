package com.opencontacts.mapgraph.data.repository

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test
class ContactRepositoryTest {

    @Test
    fun normalizePhoneNumber_removesNonDigits() {
        val testCases = listOf(
            "+1 (555) 123-4567" to "15551234567",
            "555-123-4567" to "5551234567",
            "(555) 123 4567" to "5551234567",
            "+49 30 1234567" to "49301234567",
            "123abc456" to "123456",
        )

        testCases.forEach { (input, expected) ->
            assertEquals(expected, normalizePhoneNumber(input))
        }
    }

    @Test
    fun normalizePhoneNumber_returnsNullWhenNoDigitsExist() {
        assertNull(normalizePhoneNumber(""))
        assertNull(normalizePhoneNumber("ext."))
        assertNull(normalizePhoneNumber(null))
    }

    @Test
    fun formatStructuredAddress_skipsBlankSegments() {
        assertEquals(
            "123 Main St, Berlin 10115, Germany",
            formatStructuredAddress(
                street = "123 Main St",
                city = "Berlin",
                state = "",
                postalCode = "10115",
                country = "Germany",
            ),
        )
        assertEquals(
            "Sydney, NSW 2000, Australia",
            formatStructuredAddress(
                street = null,
                city = "Sydney",
                state = "NSW",
                postalCode = "2000",
                country = "Australia",
            ),
        )
        assertNull(formatStructuredAddress(null, null, null, null, null))
    }
}
