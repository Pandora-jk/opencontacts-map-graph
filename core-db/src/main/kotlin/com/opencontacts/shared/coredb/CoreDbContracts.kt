package com.opencontacts.shared.coredb

public data class GeoRecord(
    val recordId: String,
    val sourceId: String,
    val sourceType: String,
    val latitude: Double,
    val longitude: Double,
    val updatedAtEpochMs: Long,
)

public data class GeoBounds(
    val minLatitude: Double,
    val maxLatitude: Double,
    val minLongitude: Double,
    val maxLongitude: Double,
)

public interface SharedGeoStore {
    public fun upsert(records: List<GeoRecord>)
    public fun findByRecordId(recordId: String): GeoRecord?
    public fun queryByBounds(bounds: GeoBounds): List<GeoRecord>
}

public object SharedGeoStores {
    public fun inMemory(): SharedGeoStore = InMemorySharedGeoStore()
}

internal class InMemorySharedGeoStore : SharedGeoStore {
    private val records = linkedMapOf<String, GeoRecord>()

    override fun upsert(records: List<GeoRecord>) {
        records.forEach { record -> this.records[record.recordId] = record }
    }

    override fun findByRecordId(recordId: String): GeoRecord? = records[recordId]

    override fun queryByBounds(bounds: GeoBounds): List<GeoRecord> {
        return records.values.filter { record ->
            record.latitude in bounds.minLatitude..bounds.maxLatitude &&
                record.longitude in bounds.minLongitude..bounds.maxLongitude
        }
    }
}
