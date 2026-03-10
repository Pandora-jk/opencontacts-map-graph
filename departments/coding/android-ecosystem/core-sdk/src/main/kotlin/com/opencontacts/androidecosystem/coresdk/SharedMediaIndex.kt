package com.opencontacts.androidecosystem.coresdk

data class MediaAsset(
    val mediaId: String,
    val mimeType: String,
    val checksum: String,
    val capturedAtEpochMs: Long?,
    val geoPoint: GeoCoordinate?,
)

class SharedMediaIndex {
    private val media = linkedMapOf<String, MediaAsset>()

    fun upsert(asset: MediaAsset?) {
        if (asset == null) return
        media[asset.mediaId] = asset
    }

    fun findByMediaId(mediaId: String?): MediaAsset? {
        val normalizedId = mediaId.normalizedId() ?: return null
        return media[normalizedId]
    }

    fun findGeoTagged(): List<MediaAsset> = media.values.filter { it.geoPoint != null }

    fun remove(mediaId: String?): Boolean {
        val normalizedId = mediaId.normalizedId() ?: return false
        return media.remove(normalizedId) != null
    }

    fun size(): Int = media.size

    fun clear() {
        media.clear()
    }

    private fun String?.normalizedId(): String? = this?.trim()?.takeIf { it.isNotEmpty() }
}
