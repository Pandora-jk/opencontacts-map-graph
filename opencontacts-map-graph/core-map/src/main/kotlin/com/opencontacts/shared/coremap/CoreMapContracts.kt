package com.opencontacts.shared.coremap

import java.util.LinkedHashMap

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

public enum class MapTileSource {
    CACHE,
    REMOTE,
}

public data class MapTileCacheStats(
    val hits: Int,
    val misses: Int,
    val evictions: Int,
)

public data class MapTileLoadResult(
    val payload: MapTilePayload,
    val source: MapTileSource,
)

public fun interface SharedTileFetcher {
    public fun fetch(key: MapTileKey): MapTilePayload?
}

public interface SharedTileCache {
    public fun read(key: MapTileKey): MapTilePayload?
    public fun write(key: MapTileKey, payload: MapTilePayload)
    public fun remove(key: MapTileKey)
    public fun size(): Int
}

public interface SharedTileCacheManager : SharedTileCache {
    public fun load(key: MapTileKey, fetcher: SharedTileFetcher): MapTileLoadResult?
    public fun readOffline(key: MapTileKey): MapTilePayload?
    public fun stats(): MapTileCacheStats
}

public object SharedTileCaches {
    public fun inMemory(): SharedTileCache = InMemorySharedTileCache()
    public fun manager(maxEntries: Int = DEFAULT_MAX_ENTRIES): SharedTileCacheManager {
        return InMemorySharedTileCacheManager(maxEntries = maxEntries)
    }

    public const val DEFAULT_MAX_ENTRIES: Int = 256
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

internal class InMemorySharedTileCacheManager(
    private val maxEntries: Int,
) : SharedTileCacheManager {
    private val cache = LinkedHashMap<MapTileKey, MapTilePayload>(16, 0.75f, true)
    private var hitCount: Int = 0
    private var missCount: Int = 0
    private var evictionCount: Int = 0

    init {
        require(maxEntries > 0) { "maxEntries must be > 0" }
    }

    override fun load(key: MapTileKey, fetcher: SharedTileFetcher): MapTileLoadResult? {
        val cached = cache[key]
        if (cached != null) {
            hitCount += 1
            return MapTileLoadResult(payload = cached, source = MapTileSource.CACHE)
        }

        missCount += 1
        val remote = fetcher.fetch(key) ?: return null
        write(key, remote)
        return MapTileLoadResult(payload = remote, source = MapTileSource.REMOTE)
    }

    override fun readOffline(key: MapTileKey): MapTilePayload? {
        val cached = cache[key]
        if (cached != null) {
            hitCount += 1
            return cached
        }

        missCount += 1
        return null
    }

    override fun read(key: MapTileKey): MapTilePayload? = cache[key]

    override fun write(key: MapTileKey, payload: MapTilePayload) {
        cache[key] = payload
        trimToSize()
    }

    override fun remove(key: MapTileKey) {
        cache.remove(key)
    }

    override fun size(): Int = cache.size

    override fun stats(): MapTileCacheStats {
        return MapTileCacheStats(
            hits = hitCount,
            misses = missCount,
            evictions = evictionCount,
        )
    }

    private fun trimToSize() {
        while (cache.size > maxEntries) {
            val eldest = cache.entries.firstOrNull() ?: return
            cache.remove(eldest.key)
            evictionCount += 1
        }
    }
}
