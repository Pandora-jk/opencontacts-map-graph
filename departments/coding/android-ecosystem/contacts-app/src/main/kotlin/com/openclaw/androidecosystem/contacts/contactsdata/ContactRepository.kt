package com.openclaw.androidecosystem.contacts.contactsdata

import kotlinx.coroutines.flow.Flow

enum class ContactSyncStatus {
    SUCCESS,
    PERMISSION_DENIED,
    NO_CONTACTS
}

data class ContactSyncResult(
    val status: ContactSyncStatus,
    val syncedCount: Int = 0,
    val skippedCount: Int = 0
)

interface ContactRepository {
    fun observeContacts(): Flow<List<ContactEntity>>

    suspend fun getContact(id: Long): ContactEntity?

    suspend fun upsertContact(contact: ContactEntity): Long

    suspend fun deleteContact(contact: ContactEntity)

    suspend fun searchByName(query: String): List<ContactEntity>

    suspend fun searchByPhone(query: String): List<ContactEntity>

    suspend fun searchByEmail(query: String): List<ContactEntity>

    suspend fun getFrequentContacts(limit: Int): List<ContactEntity>

    suspend fun syncSystemContacts(): ContactSyncResult
}
