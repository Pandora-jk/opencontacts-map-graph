package com.opencontacts.shared.coremedia

public data class MediaGeoPoint(
    val latitude: Double,
    val longitude: Double,
)

public data class MediaAsset(
    val mediaId: String,
    val mimeType: String,
    val checksum: String,
    val capturedAtEpochMs: Long?,
    val geoPoint: MediaGeoPoint?,
)

public interface SharedMediaIndex {
    public fun upsert(asset: MediaAsset)
    public fun findByMediaId(mediaId: String): MediaAsset?
    public fun findGeoTagged(): List<MediaAsset>
}

public object SharedMediaIndexes {
    public fun inMemory(): SharedMediaIndex = InMemorySharedMediaIndex()
}

internal class InMemorySharedMediaIndex : SharedMediaIndex {
    private val assets = linkedMapOf<String, MediaAsset>()

    override fun upsert(asset: MediaAsset) {
        assets[asset.mediaId] = asset
    }

    override fun findByMediaId(mediaId: String): MediaAsset? = assets[mediaId]

    override fun findGeoTagged(): List<MediaAsset> {
        return assets.values.filter { it.geoPoint != null }
    }
}
