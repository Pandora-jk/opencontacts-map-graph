package com.opencontacts.shared.coremedia

data class MediaGeoPoint(
    val latitude: Double,
    val longitude: Double,
)

data class MediaAsset(
    val mediaId: String,
    val mimeType: String,
    val checksum: String,
    val capturedAtEpochMs: Long?,
    val geoPoint: MediaGeoPoint?,
)

interface SharedMediaIndex {
    fun upsert(asset: MediaAsset)
    fun findByMediaId(mediaId: String): MediaAsset?
    fun findGeoTagged(): List<MediaAsset>
}

class InMemorySharedMediaIndex : SharedMediaIndex {
    private val assets = linkedMapOf<String, MediaAsset>()

    override fun upsert(asset: MediaAsset) {
        assets[asset.mediaId] = asset
    }

    override fun findByMediaId(mediaId: String): MediaAsset? = assets[mediaId]

    override fun findGeoTagged(): List<MediaAsset> {
        return assets.values.filter { it.geoPoint != null }
    }
}
