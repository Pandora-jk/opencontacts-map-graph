package com.opencontacts.androidecosystem.coresdk

class SharedTileCacheManager(
    private val maxEntries: Int = 100
) {
    init {
        require(maxEntries > 0) { "maxEntries must be positive" }
    }

    private val cache = linkedMapOf<String, ByteArray>()

    fun get(tileId: String?): ByteArray? {
        val normalizedId = tileId.normalizedId() ?: return null
        return cache[normalizedId]?.copyOf()
    }

    fun put(tileId: String?, data: ByteArray?): Boolean {
        val normalizedId = tileId.normalizedId() ?: return false
        if (data == null || data.isEmpty()) return false
        
        cache.remove(normalizedId)
        cache[normalizedId] = data.copyOf()
        
        while (cache.size > maxEntries) {
            cache.remove(cache.keys.first())
        }
        
        return true
    }

    fun contains(tileId: String?): Boolean {
        val normalizedId = tileId.normalizedId() ?: return false
        return cache.containsKey(normalizedId)
    }

    fun size(): Int = cache.size

    fun clear() {
        cache.clear()
    }

    private fun String?.normalizedId(): String? = this?.trim()?.takeIf { it.isNotEmpty() }
}
