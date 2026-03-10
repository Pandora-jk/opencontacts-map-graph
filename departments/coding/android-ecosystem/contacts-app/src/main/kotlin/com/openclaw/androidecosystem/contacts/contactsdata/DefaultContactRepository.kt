package com.openclaw.androidecosystem.contacts.contactsdata

import kotlinx.coroutines.flow.Flow
import kotlin.math.max
import kotlin.math.min

class DefaultContactRepository(
    private val contactDao: ContactDao,
    private val permissionChecker: ContactsPermissionChecker,
    private val systemContactDataSource: SystemContactDataSource
) : ContactRepository {

    override fun observeContacts(): Flow<List<ContactEntity>> = contactDao.observeAll()

    override suspend fun getContact(id: Long): ContactEntity? = contactDao.getById(id)

    override suspend fun upsertContact(contact: ContactEntity): Long {
        return contactDao.insert(contact)
    }

    override suspend fun deleteContact(contact: ContactEntity) {
        contactDao.delete(contact)
    }

    override suspend fun searchByName(query: String): List<ContactEntity> = contactDao.queryByName(query.trim())

    override suspend fun searchByPhone(query: String): List<ContactEntity> =
        contactDao.queryByPhone(normalizePhoneQuery(query))

    override suspend fun searchByEmail(query: String): List<ContactEntity> = contactDao.queryByEmail(query.trim())

    override suspend fun getFrequentContacts(limit: Int): List<ContactEntity> =
        contactDao.getFrequentContacts(limit.coerceAtLeast(1))

    override suspend fun syncSystemContacts(): ContactSyncResult {
        if (!permissionChecker.hasContactsPermission()) {
            return ContactSyncResult(status = ContactSyncStatus.PERMISSION_DENIED)
        }

        val sourceContacts = systemContactDataSource.fetchContacts()
        if (sourceContacts.isEmpty()) {
            return ContactSyncResult(status = ContactSyncStatus.NO_CONTACTS)
        }

        val deduplicatedContacts = sourceContacts.distinctBy(::systemContactKey)
        val existingContacts = contactDao.getAll()

        var syncedCount = 0
        val skippedCount = sourceContacts.size - deduplicatedContacts.size

        deduplicatedContacts.forEach { record ->
            val contact = record.toContactEntity()
            val existing = existingContacts.firstOrNull { matches(it, contact) }
            if (existing == null) {
                contactDao.insert(contact)
            } else {
                contactDao.update(
                    contact.copy(
                        id = existing.id,
                        connectionStrength = max(existing.connectionStrength, contact.connectionStrength)
                    )
                )
            }
            syncedCount += 1
        }

        return ContactSyncResult(
            status = ContactSyncStatus.SUCCESS,
            syncedCount = syncedCount,
            skippedCount = skippedCount
        )
    }

    private fun matches(existing: ContactEntity, incoming: ContactEntity): Boolean {
        val existingPhone = normalizePhoneQuery(existing.phone.orEmpty())
        val incomingPhone = normalizePhoneQuery(incoming.phone.orEmpty())
        return when {
            existingPhone.isNotEmpty() && existingPhone == incomingPhone -> true
            !existing.email.isNullOrBlank() && existing.email.equals(incoming.email, ignoreCase = true) -> true
            else -> existing.displayName.equals(incoming.displayName, ignoreCase = true)
        }
    }

    private fun systemContactKey(record: SystemContactRecord): String {
        val phone = normalizePhoneQuery(record.phone.orEmpty())
        val email = record.email.orEmpty().trim().lowercase()
        val name = record.displayName.orEmpty().trim().lowercase()
        return listOf(phone, email, name).firstOrNull { it.isNotBlank() } ?: name
    }

    private fun SystemContactRecord.toContactEntity(): ContactEntity {
        return ContactEntity(
            displayName = displayName?.takeIf { it.isNotBlank() } ?: "Unknown Contact",
            phone = phone?.takeIf { it.isNotBlank() },
            email = email?.takeIf { it.isNotBlank() },
            photoUri = photoUri?.takeIf { it.isNotBlank() },
            lastContacted = lastContacted,
            connectionStrength = calculateStrength(interactionCount, lastContacted)
        )
    }

    private fun calculateStrength(interactionCount: Int, lastContacted: Long?): Int {
        val activityScore = interactionCount.coerceAtLeast(0) * 8
        val recencyScore = when {
            lastContacted == null -> 0
            System.currentTimeMillis() - lastContacted <= DAY_MS * 7 -> 25
            System.currentTimeMillis() - lastContacted <= DAY_MS * 30 -> 15
            else -> 5
        }
        return min(100, activityScore + recencyScore)
    }

    private fun normalizePhoneQuery(phone: String): String {
        return phone.filter(Char::isDigit)
    }

    private companion object {
        const val DAY_MS = 24L * 60L * 60L * 1000L
    }
}
