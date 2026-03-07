package com.opencontacts.mapgraph.data.local.dao

import androidx.room.*
import com.opencontacts.mapgraph.data.local.entity.ContactEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface ContactDao {
    
    @Query("SELECT * FROM contacts ORDER BY displayName ASC")
    fun getAllContacts(): Flow<List<ContactEntity>>
    
    @Query("SELECT * FROM contacts ORDER BY displayName ASC")
    suspend fun getAllContactsSync(): List<ContactEntity>>
    
    @Query("SELECT * FROM contacts WHERE id = :id")
    suspend fun getContactById(id: Long): ContactEntity?
    
    @Query("SELECT * FROM contacts WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
    fun getContactsWithCoordinates(): Flow<List<ContactEntity>>
    
    @Query("SELECT * FROM contacts WHERE addressFormatted IS NOT NULL AND (latitude IS NULL OR longitude IS NULL)")
    suspend fun getContactsNeedingGeocoding(): List<ContactEntity>>
    
    @Query("SELECT COUNT(*) FROM contacts WHERE latitude IS NULL AND addressFormatted IS NOT NULL")
    suspend fun getPendingGeocodingCount(): Int
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertContact(contact: ContactEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertContacts(contacts: List<ContactEntity>)
    
    @Update
    suspend fun updateContact(contact: ContactEntity)
    
    @Query("UPDATE contacts SET latitude = :lat, longitude = :lng, geocodingTimestamp = :timestamp WHERE id = :id")
    suspend fun updateContactCoordinates(id: Long, lat: Double?, lng: Double?, timestamp: Long)
    
    @Delete
    suspend fun deleteContact(contact: ContactEntity)
    
    @Query("DELETE FROM contacts")
    suspend fun deleteAll()
    
    @Query("SELECT * FROM contacts WHERE displayName LIKE :query OR phoneNumber LIKE :query")
    fun searchContacts(query: String): Flow<List<ContactEntity>>
}
