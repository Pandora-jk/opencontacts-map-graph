package com.opencontacts.androidecosystem.coresdk

data class GeoCoordinate(
    val latitude: Double,
    val longitude: Double,
)

class SharedGeoStore {
    private val coordinates = linkedMapOf<String, GeoCoordinate>()

    fun isReady(): Boolean = true

    fun put(id: String?, latitude: Double?, longitude: Double?): Boolean {
        val normalizedId = id.normalizedId() ?: return false
        if (!latitude.isValidLatitude() || !longitude.isValidLongitude()) {
            return false
        }
        coordinates[normalizedId] = GeoCoordinate(latitude!!, longitude!!)
        return true
    }

    fun get(id: String?): GeoCoordinate? {
        val normalizedId = id.normalizedId() ?: return null
        return coordinates[normalizedId]
    }

    fun remove(id: String?): Boolean {
        val normalizedId = id.normalizedId() ?: return false
        return coordinates.remove(normalizedId) != null
    }

    fun all(): Map<String, GeoCoordinate> = coordinates.toMap()

    fun size(): Int = coordinates.size

    fun clear() {
        coordinates.clear()
    }

    private fun String?.normalizedId(): String? = this?.trim()?.takeIf { it.isNotEmpty() }

    private fun Double?.isValidLatitude(): Boolean = this != null && this in -90.0..90.0

    private fun Double?.isValidLongitude(): Boolean = this != null && this in -180.0..180.0
}
