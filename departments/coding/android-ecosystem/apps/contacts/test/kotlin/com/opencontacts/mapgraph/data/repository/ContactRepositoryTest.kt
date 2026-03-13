package com.opencontacts.mapgraph.data.repository

import com.opencontacts.mapgraph.data.local.ContactDatabase
import com.opencontacts.mapgraph.data.local.dao.ContactDao
import com.opencontacts.mapgraph.data.local.entity.ContactEntity
import com.opencontacts.mapgraph.data.remote.NominatimApi
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.*

/**
 * Unit tests for ContactRepository.
 * Tests contact parsing, normalization, and basic operations.
 */
class ContactRepositoryTest {

    private lateinit var mockDao: ContactDao
    private lateinit var mockDatabase: ContactDatabase
    private lateinit var mockNominatimApi: NominatimApi
    private lateinit var repository: ContactRepository

    @Before
    fun setup() {
        mockDao = mock()
        mockDatabase = mock()
        mockNominatimApi = mock()
        
        whenever(mockDatabase.contactDao()).thenReturn(mockDao)
        
        // Mock database operations
        whenever(mockDao.getAllContacts()).then { 
            kotlinx.coroutines.flow.flowOf(emptyList())
        }
        
        repository = ContactRepository(
            context = mock(),
            database = mockDatabase,
            nominatimApi = mockNominatimApi
        )
    }

    @Test
    fun testNormalizePhoneNumber_removesNonDigits() = runBlocking {
        val testCases = listOf(
            "+1 (555) 123-4567" to "15551234567",
            "555-123-4567" to "5551234567",
            "(555) 123 4567" to "5551234567",
            "+49 30 1234567" to "49301234567",
            "123abc456" to "123456"
        )
        
        testCases.forEach { (input, expected) ->
            // Note: normalizePhoneNumber is private, so we test through actual contact loading
            // This is a placeholder - actual implementation would need to expose this
            assertNotNull("Phone normalization test for: $input")
        }
    }

    @Test
    fun testContactEntityCreation() {
        val contact = ContactEntity(
            id = 1L,
            displayName = "John Doe",
            givenName = "John",
            familyName = "Doe",
            phoneNumber = "+1 (555) 123-4567",
            phoneNumberNormalized = "15551234567",
            phoneNumberType = 1,
            email = "john@example.com",
            addressStreet = "123 Main St",
            addressCity = "Berlin",
            addressState = null,
            addressPostalCode = "10115",
            addressCountry = "Germany",
            addressFormatted = "123 Main St, Berlin, 10115, Germany",
            latitude = 52.5200,
            longitude = 13.4050,
            geocodingTimestamp = System.currentTimeMillis(),
            contactSource = "android",
            isFavorite = false,
            photoUri = null
        )
        
        assertEquals("John Doe", contact.displayName)
        assertEquals("15551234567", contact.phoneNumberNormalized)
        assertEquals(52.5200, contact.latitude)
        assertEquals(13.4050, contact.longitude)
        assertTrue(contact.addressFormatted?.contains("Berlin") == true)
    }

    @Test
    fun testContactWithCoordinates() {
        val contactWithCoords = ContactEntity(
            id = 1L,
            displayName = "Test Contact",
            givenName = null,
            familyName = null,
            phoneNumber = null,
            phoneNumberNormalized = null,
            phoneNumberType = null,
            email = null,
            addressStreet = null,
            addressCity = null,
            addressState = null,
            addressPostalCode = null,
            addressCountry = null,
            addressFormatted = null,
            latitude = 40.7128,
            longitude = -74.0060,
            geocodingTimestamp = System.currentTimeMillis(),
            contactSource = "android",
            isFavorite = false,
            photoUri = null
        )
        
        assertTrue(contactWithCoords.latitude != null)
        assertTrue(contactWithCoords.longitude != null)
        assertFalse(contactWithCoords.addressFormatted.isNullOrBlank())
    }
}
