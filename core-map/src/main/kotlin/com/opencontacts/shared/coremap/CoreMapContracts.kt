package com.opencontacts.shared.coremap

data class MapTileKey(
    val zoom: Int,
    val x: Int,
    val y: Int,
    val style: String,
)

data class MapTilePayload(
    val bytes: ByteArray,
    val etag: String?,
    val fetchedAtEpochMs: Long,
)

interface SharedTileCache {
    fun read(key: MapTileKey): MapTilePayload?
    fun write(key: MapTileKey, payload: MapTilePayload)
    fun remove(key: MapTileKey)
    fun size(): Int
}

class InMemorySharedTileCache : SharedTileCache {
    private val cache = linkedMapOf<MapTileKey, MapTilePayload>()

    override fun read(key: MapTileKey): MapTilePayload? = cache[key]

    override fun write(key: MapTileKey, payload: MapTilePayload) {
        cache[key] = payload
    }

    override fun remove(key: MapTileKey) {
        cache.remove(key)
    }

    override fun size(): Int = cache.size
}
