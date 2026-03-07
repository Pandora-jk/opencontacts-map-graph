package com.opencontacts.mapgraph.data.repository

import android.Manifest
import android.content.ContentResolver
import android.content.Context
import android.provider.ContactsContract
import com.opencontacts.mapgraph.data.local.ContactDatabase
import com.opencontacts.mapgraph.data.local.entity.ContactEntity
import com.opencontacts.mapgraph.data.remote.NominatimApi
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext

/**
 * Repository for managing contact data.
 * Handles:
 * - Direct ContentResolver queries (no sync adapters)
 * - Room database caching
 * - Batch geocoding with Nominatim API
 */
class ContactRepository(
    private val context: Context,
    private val database: ContactDatabase,
    private val nominatimApi: NominatimApi = NominatimApi()
) {
    private val dao = database.contactDao()
    
    /**
     * Get all contacts as a Flow for reactive UI updates.
     */
    fun getAllContactsFlow(): Flow<List<ContactEntity>> = dao.getAllContacts()
    
    /**
     * Get contacts with valid coordinates for map display.
     */
    fun getContactsWithCoordinatesFlow(): Flow<List<ContactEntity>> = dao.getContactsWithCoordinates()
    
    /**
     * Search contacts by name or phone number.
     */
    fun searchContacts(query: String): Flow<List<ContactEntity>> = dao.searchContacts("%$query%")
    
    /**
     * Load contacts from Android's ContentResolver directly.
     * Minimal permissions: only READ_CONTACTS required.
     */
    suspend fun loadContactsFromSystem(): Result<LoadResult> = withContext(Dispatchers.IO) {
        try {
            val contentResolver = context.contentResolver
            val contacts = mutableListOf<ContactEntity>()
            
            // Query contacts with minimal required fields
            val cursor = contentResolver.query(
                ContactsContract.Contacts.CONTENT_URI,
                arrayOf(
                    ContactsContract.Contacts._ID,
                    ContactsContract.Contacts.DISPLAY_NAME,
                    ContactsContract.Contacts.HAS_PHONE_NUMBER,
                    ContactsContract.Contacts.PHOTO_URI
                ),
                null,
                null,
                null
            )
            
            cursor?.use {
                while (it.moveToNext()) {
                    val id = it.getLong(0)
                    val displayName = it.getString(1) ?: ""
                    val hasPhone = it.getInt(2)
                    val photoUri = it.getString(3)
                    
                    // Get phone number
                    var phoneNumber: String? = null
                    var phoneNumberType: Int? = null
                    if (hasPhone > 0) {
                        val phoneCursor = contentResolver.query(
                            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                            arrayOf(
                                ContactsContract.CommonDataKinds.Phone.NUMBER,
                                ContactsContract.CommonDataKinds.Phone.TYPE
                            ),
                            "${ContactsContract.CommonDataKinds.Phone.CONTACT_ID} = ?",
                            arrayOf(id.toString()),
                            null
                        )
                        
                        phoneCursor?.use { pc ->
                            if (pc.moveToFirst()) {
                                phoneNumber = pc.getString(0)
                                phoneNumberType = pc.getInt(1)
                            }
                        }
                    }
                    
                    // Get email
                    var email: String? = null
                    val emailCursor = contentResolver.query(
                        ContactsContract.CommonDataKinds.Email.CONTENT_URI,
                        arrayOf(ContactsContract.CommonDataKinds.Email.DATA),
                        "${ContactsContract.CommonDataKinds.Email.CONTACT_ID} = ?",
                        arrayOf(id.toString()),
                        null
                    )
                    
                    emailCursor?.use { ec ->
                        if (ec.moveToFirst()) {
                            email = ec.getString(0)
                        }
                    }
                    
                    // Get address
                    var addressStreet: String? = null
                    var addressCity: String? = null
                    var addressState: String? = null
                    var addressPostalCode: String? = null
                    var addressCountry: String? = null
                    var addressFormatted: String? = null
                    
                    val addressCursor = contentResolver.query(
                        ContactsContract.CommonDataKinds.StructuredPostal.CONTENT_URI,
                        arrayOf(
                            ContactsContract.CommonDataKinds.StructuredPostal.STREET,
                            ContactsContract.CommonDataKinds.StructuredPostal.CITY,
                            ContactsContract.CommonDataKinds.StructuredPostal.REGION,
                            ContactsContract.CommonDataKinds.StructuredPostal.POSTCODE,
                            ContactsContract.CommonDataKinds.StructuredPostal.COUNTRY
                        ),
                        "${ContactsContract.CommonDataKinds.StructuredPostal.CONTACT_ID} = ?",
                        arrayOf(id.toString()),
                        null
                    )
                    
                    addressCursor?.use { ac ->
                        if (ac.moveToFirst()) {
                            addressStreet = ac.getString(0)
                            addressCity = ac.getString(1)
                            addressState = ac.getString(2)
                            addressPostalCode = ac.getString(3)
                            addressCountry = ac.getString(4)
                            
                            // Build formatted address
                            addressFormatted = buildString {
                                if (!addressStreet.isNullOrBlank()) {
                                    append(addressStreet)
                                }
                                if (!addressCity.isNullOrBlank()) {
                                    if (isNotEmpty()) append(", "
                                    append(addressCity)
                                }
                                if (!addressState.isNullOrBlank()) {
                                    if (isNotEmpty()) append(", "
                                    append(addressState)
                                }
                                if (!addressPostalCode.isNullOrBlank()) {
                                    if (isNotEmpty()) append(" "
                                    append(addressPostalCode)
                                }
                                if (!addressCountry.isNullOrBlank()) {
                                    if (isNotEmpty()) append(", "
                                    append(addressCountry)
                                }
                            }.trim().trimEnd(',')
                        }
                    }
                    
                    val contact = ContactEntity(
                        id = id,
                        displayName = displayName,
                        givenName = null,
                        familyName = null,
                        phoneNumber = phoneNumber,
                        phoneNumberNormalized = phoneNumber?.let { normalizePhoneNumber(it) },
                        phoneNumberType = phoneNumberType,
                        email = email,
                        addressStreet = addressStreet,
                        addressCity = addressCity,
                        addressState = addressState,
                        addressPostalCode = addressPostalCode,
                        addressCountry = addressCountry,
                        addressFormatted = addressFormatted,
                        latitude = null,
                        longitude = null,
                        geocodingTimestamp = null,
                        contactSource = "android",
                        isFavorite = false,
                        photoUri = photoUri
                    )
                    
                    contacts.add(contact)
                }
            }
            
            // Cache in database
            dao.insertContacts(contacts)
            
            Result.success(
                LoadResult(
                    loaded = contacts.size,
                    failed = 0,
                    geocodingPending = contacts.count { !it.addressFormatted.isNullOrBlank() }
                )
            )
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Geocode contacts that have addresses but no coordinates.
     * Rate-limited to comply with Nominatim policy.
     */
    suspend fun geocodePendingContacts(): Result<GeocodeResult> = withContext(Dispatchers.IO) {
        try {
            val pendingContacts = dao.getContactsNeedingGeocoding()
            if (pendingContacts.isEmpty()) {
                return@withContext Result.success(GeocodeResult(geocoded = 0, failed = 0))
            }
            
            var geocoded = 0
            var failed = 0
            
            pendingContacts.forEach { contact ->
                val address = contact.addressFormatted
                if (!address.isNullOrBlank()) {
                    val result = nominatimApi.geocodeAddress(address)
                    result.fold(
                        onSuccess = { coords ->
                            if (coords != null) {
                                dao.updateContactCoordinates(
                                    contact.id,
                                    coords.latitude,
                                    coords.longitude,
                                    System.currentTimeMillis()
                                )
                                geocoded++
                            } else {
                                failed++
                            }
                        },
                        onFailure = {
                            failed++
                        }
                    )
                }
            }
            
            Result.success(GeocodeResult(geocoded, failed))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    /**
     * Get count of contacts pending geocoding.
     */
    suspend fun getGeocodingPendingCount(): Int = dao.getPendingGeocodingCount()
    
    /**
     * Normalize phone number by removing non-digit characters.
     */
    private fun normalizePhoneNumber(phone: String): String {
        return phone.filter { it.isDigit() }
    }
    
    data class LoadResult(
        val loaded: Int,
        val failed: Int,
        val geocodingPending: Int
    )
    
    data class GeocodeResult(
        val geocoded: Int,
        val failed: Int
    )
}
