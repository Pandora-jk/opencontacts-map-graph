package com.openclaw.androidecosystem.contacts.contactsmap

data class GeoCoordinate(
    val latitude: Double,
    val longitude: Double
) {
    init {
        require(latitude in -90.0..90.0) { "Latitude must be within [-90, 90]." }
        require(longitude in -180.0..180.0) { "Longitude must be within [-180, 180]." }
    }
}
