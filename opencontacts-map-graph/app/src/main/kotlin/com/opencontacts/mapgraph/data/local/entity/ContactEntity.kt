package com.opencontacts.mapgraph.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Contact entity stored in Room database.
 * Contains geocoded coordinates for map visualization.
 */
@Entity(tableName = "contacts")
data class ContactEntity(
    @PrimaryKey val id: Long,
    val displayName: String,
    val givenName: String?,
    val familyName: String?,
    val phoneNumber: String?,
    val phoneNumberNormalized: String?,
    val phoneNumberType: Int?,
    val email: String?,
    val addressStreet: String?,
    val addressCity: String?,
    val addressState: String?,
    val addressPostalCode: String?,
    val addressCountry: String?,
    val addressFormatted: String?,
    val latitude: Double?,
    val longitude: Double?,
    val geocodingTimestamp: Long?,
    val contactSource: String?,
    val isFavorite: Boolean = false,
    val photoUri: String?,
    val lastUpdated: Long = System.currentTimeMillis()
)
