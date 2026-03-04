package com.opencontacts.mapgraph.data.repository

import com.opencontacts.shared.coredb.InMemorySharedGeoStore
import com.opencontacts.shared.coredb.SharedGeoStore
import com.opencontacts.shared.coremap.InMemorySharedTileCache
import com.opencontacts.shared.coremap.SharedTileCache
import com.opencontacts.shared.coremedia.InMemorySharedMediaIndex
import com.opencontacts.shared.coremedia.SharedMediaIndex
import com.opencontacts.shared.coresync.InMemorySharedSyncScheduler
import com.opencontacts.shared.coresync.SharedSyncScheduler

/**
 * Temporary in-memory composition root for shared core contracts.
 * Concrete Android-backed implementations will replace these during integration tasks.
 */
data class SharedCoreRegistry(
    val geoStore: SharedGeoStore,
    val tileCache: SharedTileCache,
    val mediaIndex: SharedMediaIndex,
    val syncScheduler: SharedSyncScheduler,
) {
    companion object {
        fun inMemory(): SharedCoreRegistry {
            return SharedCoreRegistry(
                geoStore = InMemorySharedGeoStore(),
                tileCache = InMemorySharedTileCache(),
                mediaIndex = InMemorySharedMediaIndex(),
                syncScheduler = InMemorySharedSyncScheduler(),
            )
        }
    }
}
