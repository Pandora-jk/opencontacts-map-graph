package com.opencontacts.androidecosystem.contacts.data

enum class ContactSyncStatus {
    SUCCESS,
    PERMISSION_DENIED,
}

data class ContactSyncResult(
    val status: ContactSyncStatus,
    val syncedCount: Int = 0,
)

fun interface ContactsPermissionChecker {
    fun hasContactsPermission(): Boolean
}

fun interface SystemContactsSyncer {
    suspend fun syncContacts(): Int
}

class StubSystemContactsSyncer : SystemContactsSyncer {
    override suspend fun syncContacts(): Int = 0
}

class ContactRepository(
    private val contactDao: ContactDao,
    private val permissionChecker: ContactsPermissionChecker = ContactsPermissionChecker { false },
    private val systemContactsSyncer: SystemContactsSyncer = StubSystemContactsSyncer(),
) {
    suspend fun insert(contact: ContactEntity): Long = contactDao.insert(contact)

    suspend fun update(contact: ContactEntity) {
        contactDao.update(contact)
    }

    suspend fun delete(contact: ContactEntity) {
        contactDao.delete(contact)
    }

    suspend fun getById(id: Long): ContactEntity? = contactDao.getById(id)

    suspend fun queryByName(name: String?): List<ContactEntity> {
        if (name.isNullOrBlank()) {
            return emptyList()
        }
        return contactDao.queryByName(name.trim())
    }

    suspend fun queryByPhone(phone: String?): List<ContactEntity> {
        if (phone.isNullOrBlank()) {
            return emptyList()
        }
        return contactDao.queryByPhone(phone.trim())
    }

    suspend fun getAll(): List<ContactEntity> = contactDao.getAll()

    suspend fun getFrequentContacts(limit: Int): List<ContactEntity> {
        if (limit <= 0) {
            return emptyList()
        }
        return contactDao.getFrequentContacts(limit)
    }

    suspend fun syncWithSystemContacts(): ContactSyncResult {
        if (!permissionChecker.hasContactsPermission()) {
            return ContactSyncResult(status = ContactSyncStatus.PERMISSION_DENIED)
        }

        return ContactSyncResult(
            status = ContactSyncStatus.SUCCESS,
            syncedCount = systemContactsSyncer.syncContacts(),
        )
    }
}
