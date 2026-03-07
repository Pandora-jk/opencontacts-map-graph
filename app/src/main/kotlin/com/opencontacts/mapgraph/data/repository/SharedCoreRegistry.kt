package com.opencontacts.mapgraph.data.repository

import com.opencontacts.shared.coredb.SharedGeoStore
import com.opencontacts.shared.coredb.SharedGeoStores
import com.opencontacts.shared.coremap.SharedTileCacheManager
import com.opencontacts.shared.coremap.SharedTileCaches
import com.opencontacts.shared.coremedia.SharedMediaIndex
import com.opencontacts.shared.coremedia.SharedMediaIndexes
import com.opencontacts.shared.coresync.SharedSyncScheduler
import com.opencontacts.shared.coresync.SharedSyncSchedulers

/**
 * Temporary in-memory composition root for shared core contracts.
 * Concrete Android-backed implementations will replace these during integration tasks.
 */
data class SharedCoreRegistry(
    val geoStore: SharedGeoStore,
    val tileCache: SharedTileCacheManager,
    val mediaIndex: SharedMediaIndex,
    val syncScheduler: SharedSyncScheduler,
) {
    companion object {
        fun inMemory(): SharedCoreRegistry {
            return SharedCoreRegistry(
                geoStore = SharedGeoStores.inMemory(),
                tileCache = SharedTileCaches.manager(),
                mediaIndex = SharedMediaIndexes.inMemory(),
                syncScheduler = SharedSyncSchedulers.inMemory(),
            )
        }
    }
}
