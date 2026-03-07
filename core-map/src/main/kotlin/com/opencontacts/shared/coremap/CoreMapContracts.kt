package com.opencontacts.shared.coremap

public data class MapTileKey(
    val zoom: Int,
    val x: Int,
    val y: Int,
    val style: String,
)

public data class MapTilePayload(
    val bytes: ByteArray,
    val etag: String?,
    val fetchedAtEpochMs: Long,
)

public interface SharedTileCache {
    public fun read(key: MapTileKey): MapTilePayload?
    public fun write(key: MapTileKey, payload: MapTilePayload)
    public fun remove(key: MapTileKey)
    public fun size(): Int
}

public object SharedTileCaches {
    public fun inMemory(): SharedTileCache = InMemorySharedTileCache()
}

internal class InMemorySharedTileCache : SharedTileCache {
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
