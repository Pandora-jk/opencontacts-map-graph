package com.opencontacts.androidecosystem.contacts.data

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update

@Dao
interface ContactDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(contact: ContactEntity): Long

    @Update
    suspend fun update(contact: ContactEntity)

    @Delete
    suspend fun delete(contact: ContactEntity)

    @Query("SELECT * FROM contacts WHERE id = :id LIMIT 1")
    suspend fun getById(id: Long): ContactEntity?

    @Query(
        """
        SELECT * FROM contacts
        WHERE :name IS NOT NULL
          AND TRIM(:name) != ''
          AND displayName LIKE '%' || TRIM(:name) || '%' COLLATE NOCASE
        ORDER BY displayName ASC, id ASC
        """,
    )
    suspend fun queryByName(name: String?): List<ContactEntity>

    @Query(
        """
        SELECT * FROM contacts
        WHERE :phone IS NOT NULL
          AND TRIM(:phone) != ''
          AND phone LIKE '%' || TRIM(:phone) || '%'
        ORDER BY displayName ASC, id ASC
        """,
    )
    suspend fun queryByPhone(phone: String?): List<ContactEntity>

    @Query("SELECT * FROM contacts ORDER BY displayName ASC, id ASC")
    suspend fun getAll(): List<ContactEntity>

    @Query(
        """
        SELECT * FROM contacts
        ORDER BY connectionStrength DESC, COALESCE(lastContacted, 0) DESC, displayName ASC, id ASC
        LIMIT :limit
        """,
    )
    suspend fun getFrequentContacts(limit: Int): List<ContactEntity>
}
