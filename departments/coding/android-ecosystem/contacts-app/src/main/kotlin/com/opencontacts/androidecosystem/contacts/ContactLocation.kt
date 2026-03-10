package com.opencontacts.androidecosystem.contacts

import kotlin.math.asin
import kotlin.math.cos
import kotlin.math.pow
import kotlin.math.sin
import kotlin.math.sqrt

data class ContactLocation(
    val contactId: String,
    val latitude: Double?,
    val longitude: Double?,
    val category: String? = null,
) {
    fun isValid(): Boolean {
        return latitude != null &&
            longitude != null &&
            latitude in -90.0..90.0 &&
            longitude in -180.0..180.0
    }

    fun normalizedCategory(): String? = category?.trim()?.lowercase()?.takeIf(String::isNotEmpty)

    fun distanceTo(other: ContactLocation?): Double? {
        if (!isValid() || other == null || !other.isValid()) {
            return null
        }
        if (latitude == other.latitude && longitude == other.longitude) {
            return 0.0
        }

        val earthRadiusKm = 6371.0
        val latitudeDelta = Math.toRadians(other.latitude!! - latitude!!)
        val longitudeDelta = Math.toRadians(other.longitude!! - longitude!!)
        val latitudeA = Math.toRadians(latitude)
        val latitudeB = Math.toRadians(other.latitude)

        val haversine = sin(latitudeDelta / 2).pow(2) +
            sin(longitudeDelta / 2).pow(2) * cos(latitudeA) * cos(latitudeB)
        val arc = 2 * asin(sqrt(haversine))
        return earthRadiusKm * arc
    }

    companion object {
        fun fromContact(contact: ContactRecord): ContactLocation? {
            val normalizedId = contact.id.trim().takeIf(String::isNotEmpty) ?: return null
            return ContactLocation(
                contactId = normalizedId,
                latitude = contact.latitude,
                longitude = contact.longitude,
                category = contact.locationCategory ?: contact.tags.firstOrNull(),
            )
        }
    }
}
