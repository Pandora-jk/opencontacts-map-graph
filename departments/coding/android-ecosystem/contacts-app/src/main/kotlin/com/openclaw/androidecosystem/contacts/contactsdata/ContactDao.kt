package com.openclaw.androidecosystem.contacts.contactsdata

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface ContactDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(contact: ContactEntity): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(contacts: List<ContactEntity>): List<Long>

    @Update
    suspend fun update(contact: ContactEntity)

    @Delete
    suspend fun delete(contact: ContactEntity)

    @Query("SELECT * FROM contacts WHERE id = :id LIMIT 1")
    suspend fun getById(id: Long): ContactEntity?

    @Query(
        "SELECT * FROM contacts WHERE displayName LIKE '%' || :name || '%' " +
            "COLLATE NOCASE ORDER BY displayName ASC"
    )
    suspend fun queryByName(name: String): List<ContactEntity>

    @Query("SELECT * FROM contacts WHERE phone LIKE '%' || :phone || '%' ORDER BY displayName ASC")
    suspend fun queryByPhone(phone: String): List<ContactEntity>

    @Query(
        "SELECT * FROM contacts WHERE email LIKE '%' || :email || '%' " +
            "COLLATE NOCASE ORDER BY displayName ASC"
    )
    suspend fun queryByEmail(email: String): List<ContactEntity>

    @Query("SELECT * FROM contacts ORDER BY displayName ASC")
    fun observeAll(): Flow<List<ContactEntity>>

    @Query("SELECT * FROM contacts ORDER BY displayName ASC")
    suspend fun getAll(): List<ContactEntity>

    @Query(
        "SELECT * FROM contacts ORDER BY connectionStrength DESC, " +
            "COALESCE(lastContacted, 0) DESC, displayName ASC LIMIT :limit"
    )
    suspend fun getFrequentContacts(limit: Int): List<ContactEntity>

    @Query("DELETE FROM contacts")
    suspend fun clear()
}
