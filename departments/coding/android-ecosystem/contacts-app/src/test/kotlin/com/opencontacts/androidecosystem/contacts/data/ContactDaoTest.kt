package com.opencontacts.androidecosystem.contacts.data

import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import kotlinx.coroutines.test.runTest
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class ContactDaoTest {
    private lateinit var database: ContactsDatabase
    private lateinit var contactDao: ContactDao

    @Before
    fun setUp() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            ContactsDatabase::class.java,
        ).allowMainThreadQueries().build()
        contactDao = database.contactDao()
    }

    @After
    fun tearDown() {
        database.close()
    }

    @Test
    fun insert_persistsContactAndReturnsGeneratedId() = runTest {
        val contact = sampleContact(displayName = "Ada Lovelace")

        val id = contactDao.insert(contact)

        val stored = contactDao.getById(id)
        assertEquals("Ada Lovelace", stored?.displayName)
        assertEquals("111-222-3333", stored?.phone)
    }

    @Test
    fun getById_returnsNullWhenContactDoesNotExist() = runTest {
        assertNull(contactDao.getById(42L))
    }

    @Test
    fun update_persistsModifiedFields() = runTest {
        val id = contactDao.insert(sampleContact(displayName = "Grace Hopper"))

        contactDao.update(
            sampleContact(
                id = id,
                displayName = "Rear Admiral Grace Hopper",
                connectionStrength = 88,
                lastContacted = 2_000L,
            ),
        )

        val updated = contactDao.getById(id)
        assertEquals("Rear Admiral Grace Hopper", updated?.displayName)
        assertEquals(88, updated?.connectionStrength)
        assertEquals(2_000L, updated?.lastContacted)
    }

    @Test
    fun delete_removesPersistedContact() = runTest {
        val id = contactDao.insert(sampleContact(displayName = "Katherine Johnson"))
        val stored = contactDao.getById(id)!!

        contactDao.delete(stored)

        assertNull(contactDao.getById(id))
    }

    @Test
    fun queryByName_matchesPartialNameCaseInsensitively() = runTest {
        contactDao.insert(sampleContact(displayName = "Alice Adams"))
        contactDao.insert(sampleContact(displayName = "Albert Brooks"))
        contactDao.insert(sampleContact(displayName = "Brenda Stone"))

        val result = contactDao.queryByName("al")

        assertEquals(listOf("Albert Brooks", "Alice Adams"), result.map { it.displayName })
    }

    @Test
    fun queryByName_returnsEmptyListForNullOrBlankInput() = runTest {
        contactDao.insert(sampleContact(displayName = "Alice Adams"))

        assertTrue(contactDao.queryByName(null).isEmpty())
        assertTrue(contactDao.queryByName("   ").isEmpty())
    }

    @Test
    fun queryByPhone_matchesPartialPhoneNumberAndSortsByName() = runTest {
        contactDao.insert(sampleContact(displayName = "Brianna", phone = "555-1000"))
        contactDao.insert(sampleContact(displayName = "Aaron", phone = "555-2000"))
        contactDao.insert(sampleContact(displayName = "Chris", phone = "777-2000"))

        val result = contactDao.queryByPhone("555")

        assertEquals(listOf("Aaron", "Brianna"), result.map { it.displayName })
    }

    @Test
    fun queryByPhone_returnsEmptyListForNullInput() = runTest {
        contactDao.insert(sampleContact(displayName = "Brianna", phone = "555-1000"))

        assertTrue(contactDao.queryByPhone(null).isEmpty())
    }

    @Test
    fun getAll_returnsContactsSortedByDisplayName() = runTest {
        contactDao.insert(sampleContact(displayName = "Charlie"))
        contactDao.insert(sampleContact(displayName = "Alice"))
        contactDao.insert(sampleContact(displayName = "Bob"))

        val result = contactDao.getAll()

        assertEquals(listOf("Alice", "Bob", "Charlie"), result.map { it.displayName })
    }

    @Test
    fun getAll_returnsEmptyListWhenDatabaseIsEmpty() = runTest {
        assertTrue(contactDao.getAll().isEmpty())
    }

    @Test
    fun getFrequentContacts_ordersByStrengthThenRecencyAndAppliesLimit() = runTest {
        contactDao.insert(sampleContact(displayName = "Old Strong", connectionStrength = 100, lastContacted = 100L))
        contactDao.insert(sampleContact(displayName = "Recent Strong", connectionStrength = 100, lastContacted = 500L))
        contactDao.insert(sampleContact(displayName = "Medium", connectionStrength = 80, lastContacted = 1_000L))
        contactDao.insert(sampleContact(displayName = "Low", connectionStrength = 10, lastContacted = 2_000L))

        val result = contactDao.getFrequentContacts(limit = 3)

        assertEquals(listOf("Recent Strong", "Old Strong", "Medium"), result.map { it.displayName })
    }

    @Test
    fun getFrequentContacts_returnsEmptyListForZeroLimit() = runTest {
        contactDao.insert(sampleContact(displayName = "Ada"))

        assertTrue(contactDao.getFrequentContacts(0).isEmpty())
    }

    @Test
    fun insert_allowsDuplicateContactDetailsAsSeparateRows() = runTest {
        val firstId = contactDao.insert(sampleContact(displayName = "Duplicate", phone = "555-0000"))
        val secondId = contactDao.insert(sampleContact(displayName = "Duplicate", phone = "555-0000"))

        val result = contactDao.queryByPhone("555-0000")

        assertEquals(2, result.size)
        assertTrue(result.any { it.id == firstId })
        assertTrue(result.any { it.id == secondId })
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
