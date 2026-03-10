package com.opencontacts.androidecosystem.contacts.data

import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ContactRepositoryTest {
    private val contactDao = mockk<ContactDao>()
    private val permissionChecker = mockk<ContactsPermissionChecker>()
    private val systemContactsSyncer = mockk<SystemContactsSyncer>()

    private val repository = ContactRepository(
        contactDao = contactDao,
        permissionChecker = permissionChecker,
        systemContactsSyncer = systemContactsSyncer,
    )

    @Test
    fun insert_delegatesToDaoAndReturnsId() = runTest {
        val contact = sampleContact()
        coEvery { contactDao.insert(contact) } returns 7L

        val result = repository.insert(contact)

        assertEquals(7L, result)
        coVerify(exactly = 1) { contactDao.insert(contact) }
    }

    @Test
    fun update_delegatesToDao() = runTest {
        val contact = sampleContact(id = 7L)
        coEvery { contactDao.update(contact) } returns Unit

        repository.update(contact)

        coVerify(exactly = 1) { contactDao.update(contact) }
    }

    @Test
    fun delete_delegatesToDao() = runTest {
        val contact = sampleContact(id = 7L)
        coEvery { contactDao.delete(contact) } returns Unit

        repository.delete(contact)

        coVerify(exactly = 1) { contactDao.delete(contact) }
    }

    @Test
    fun getById_delegatesToDao() = runTest {
        val contact = sampleContact(id = 3L)
        coEvery { contactDao.getById(3L) } returns contact

        val result = repository.getById(3L)

        assertEquals(contact, result)
        coVerify(exactly = 1) { contactDao.getById(3L) }
    }

    @Test
    fun queryByName_trimsInputBeforeDelegating() = runTest {
        val contacts = listOf(sampleContact(displayName = "Alice"))
        coEvery { contactDao.queryByName("Alice") } returns contacts

        val result = repository.queryByName("  Alice  ")

        assertEquals(contacts, result)
        coVerify(exactly = 1) { contactDao.queryByName("Alice") }
    }

    @Test
    fun queryByName_returnsEmptyListForBlankInputWithoutDaoCall() = runTest {
        val result = repository.queryByName("   ")

        assertTrue(result.isEmpty())
        coVerify(exactly = 0) { contactDao.queryByName(any()) }
    }

    @Test
    fun queryByPhone_trimsInputBeforeDelegating() = runTest {
        val contacts = listOf(sampleContact(phone = "555-0101"))
        coEvery { contactDao.queryByPhone("555") } returns contacts

        val result = repository.queryByPhone(" 555 ")

        assertEquals(contacts, result)
        coVerify(exactly = 1) { contactDao.queryByPhone("555") }
    }

    @Test
    fun queryByPhone_returnsEmptyListForNullInputWithoutDaoCall() = runTest {
        val result = repository.queryByPhone(null)

        assertTrue(result.isEmpty())
        coVerify(exactly = 0) { contactDao.queryByPhone(any()) }
    }

    @Test
    fun getAll_delegatesToDao() = runTest {
        val contacts = listOf(sampleContact(displayName = "Alice"), sampleContact(displayName = "Bob"))
        coEvery { contactDao.getAll() } returns contacts

        val result = repository.getAll()

        assertEquals(contacts, result)
        coVerify(exactly = 1) { contactDao.getAll() }
    }

    @Test
    fun getFrequentContacts_returnsEmptyListForNonPositiveLimitWithoutDaoCall() = runTest {
        val result = repository.getFrequentContacts(0)

        assertTrue(result.isEmpty())
        coVerify(exactly = 0) { contactDao.getFrequentContacts(any()) }
    }

    @Test
    fun getFrequentContacts_delegatesPositiveLimitToDao() = runTest {
        val contacts = listOf(sampleContact(displayName = "Alice", connectionStrength = 90))
        coEvery { contactDao.getFrequentContacts(2) } returns contacts

        val result = repository.getFrequentContacts(2)

        assertEquals(contacts, result)
        coVerify(exactly = 1) { contactDao.getFrequentContacts(2) }
    }

    @Test
    fun syncWithSystemContacts_returnsPermissionDeniedWhenPermissionMissing() = runTest {
        every { permissionChecker.hasContactsPermission() } returns false

        val result = repository.syncWithSystemContacts()

        assertEquals(ContactSyncStatus.PERMISSION_DENIED, result.status)
        assertEquals(0, result.syncedCount)
        verify(exactly = 1) { permissionChecker.hasContactsPermission() }
        coVerify(exactly = 0) { systemContactsSyncer.syncContacts() }
    }

    @Test
    fun syncWithSystemContacts_callsSyncerWhenPermissionGranted() = runTest {
        every { permissionChecker.hasContactsPermission() } returns true
        coEvery { systemContactsSyncer.syncContacts() } returns 12

        val result = repository.syncWithSystemContacts()

        assertEquals(ContactSyncStatus.SUCCESS, result.status)
        assertEquals(12, result.syncedCount)
        verify(exactly = 1) { permissionChecker.hasContactsPermission() }
        coVerify(exactly = 1) { systemContactsSyncer.syncContacts() }
    }

    private fun sampleContact(
        id: Long = 0,
        displayName: String = "Sample Contact",
        phone: String? = "111-222-3333",
        email: String? = "sample@example.com",
        photoUri: String? = "content://contacts/1",
        lastContacted: Long? = 1_000L,
        connectionStrength: Int = 50,
    ) = ContactEntity(
        id = id,
        displayName = displayName,
        phone = phone,
        email = email,
        photoUri = photoUri,
        lastContacted = lastContacted,
        connectionStrength = connectionStrength,
    )
}
