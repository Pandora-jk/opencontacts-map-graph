package com.openclaw.androidecosystem.contacts.contactsmap

import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.sin
import kotlin.math.sqrt

enum class LocationCategory {
    HOME,
    WORK,
    FREQUENT,
    RECENT
}

data class ContactLocation(
    val contactId: Long,
    val coordinate: GeoCoordinate,
    val category: LocationCategory,
    val label: String,
    val updatedAt: Long = System.currentTimeMillis()
) {
    fun distanceTo(target: GeoCoordinate): Double {
        val earthRadiusKm = 6371.0
        val latDistance = Math.toRadians(target.latitude - coordinate.latitude)
        val lonDistance = Math.toRadians(target.longitude - coordinate.longitude)
        val a = sin(latDistance / 2) * sin(latDistance / 2) +
            cos(Math.toRadians(coordinate.latitude)) *
            cos(Math.toRadians(target.latitude)) *
            sin(lonDistance / 2) *
            sin(lonDistance / 2)
        val c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return earthRadiusKm * c
    }

    fun isWithin(target: GeoCoordinate, maxDistanceKm: Double): Boolean {
        return distanceTo(target) <= maxDistanceKm
    }
}
