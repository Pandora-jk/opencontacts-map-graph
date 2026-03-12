package com.opencontacts.androidecosystem.contacts

import android.content.Context
import android.provider.ContactsContract
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import android.database.Cursor
import android.provider.ContactsContract.CommonDataKinds

class ContactMapViewModel : ViewModel() {
    private val _contacts = MutableLiveData<List<ContactRecord>>(emptyList())
    val contacts: LiveData<List<ContactRecord>> = _contacts

    private val _isLoading = MutableLiveData<Boolean>(false)
    val isLoading: LiveData<Boolean> = _isLoading

    private val _loadError = MutableLiveData<String?>(null)
    val loadError: LiveData<String?> = _loadError

    fun loadContacts(context: Context) {
        // Don't reload if already loaded
        if (_contacts.value?.isNotEmpty() == true) return

        viewModelScope.launch {
            _isLoading.value = true
            _loadError.value = null

            try {
                val contactList = withContext(Dispatchers.IO) {
                    loadContactsFromDeviceOptimized(context)
                }
                _contacts.value = contactList
            } catch (e: Exception) {
                _loadError.value = "Failed to load contacts: ${e.message}"
                e.printStackTrace()
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun reloadContacts(context: Context) {
        _contacts.value = emptyList()
        loadContacts(context)
    }

    /**
     * Optimized contact loading - single query for all contacts,
     * then batch queries for related data.
     */
    private fun loadContactsFromDeviceOptimized(context: Context): List<ContactRecord> {
        val contactList = mutableListOf<ContactRecord>()
        var cursor: Cursor? = null

        try {
            // Step 1: Get all contacts with basic info in ONE query
            cursor = context.contentResolver.query(
                ContactsContract.Contacts.CONTENT_URI,
                arrayOf(
                    ContactsContract.Contacts._ID,
                    ContactsContract.Contacts.DISPLAY_NAME,
                    ContactsContract.Contacts.HAS_PHONE_NUMBER,
                    ContactsContract.Contacts.STARRED,
                    ContactsContract.Contacts.PHOTO_URI
                ),
                null,
                null,
                "${ContactsContract.Contacts.DISPLAY_NAME} ASC"
            )

            val contactsById = mutableMapOf<String, ContactRecord>()
            val contactIds = mutableListOf<String>()

            cursor?.use { contactsCursor ->
                val idIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts._ID)
                val nameIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
                val hasPhoneIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts.HAS_PHONE_NUMBER)
                val starredIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts.STARRED)
                val photoUriIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts.PHOTO_URI)

                while (contactsCursor.moveToNext()) {
                    val id = contactsCursor.getString(idIndex) ?: continue
                    val name = contactsCursor.getString(nameIndex)
                    val hasPhone = contactsCursor.getInt(hasPhoneIndex)
                    val isStarred = contactsCursor.getInt(starredIndex) > 0
                    val photoUri = contactsCursor.getString(photoUriIndex)

                    contactIds.add(id)
                    contactsById[id] = ContactRecord(
                        id = id,
                        displayName = name,
                        firstName = null,
                        lastName = null,
                        email = null,
                        phoneNumbers = emptyList(),
                        company = null,
                        jobTitle = null,
                        address = null,
                        isFavorite = isStarred,
                        groups = emptyList(),
                        photoUri = photoUri
                    )
                }
            }

            if (contactIds.isEmpty()) {
                return emptyList()
            }

            // Step 2: Batch load phone numbers
            val phoneCursor = context.contentResolver.query(
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                arrayOf(
                    ContactsContract.CommonDataKinds.Phone.CONTACT_ID,
                    ContactsContract.CommonDataKinds.Phone.NUMBER
                ),
                null,
                null,
                null
            )

            phoneCursor?.use { pc ->
                val contactIdIndex = pc.getColumnIndex(ContactsContract.CommonDataKinds.Phone.CONTACT_ID)
                val numberIndex = pc.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)

                while (pc.moveToNext()) {
                    val contactId = pc.getString(contactIdIndex)
                    val phone = pc.getString(numberIndex)
                    if (!contactId.isNullOrBlank() && !phone.isNullOrBlank()) {
                        val contact = contactsById[contactId]
                        if (contact != null) {
                            contact.phoneNumbers.add(phone)
                        }
                    }
                }
            }

            // Step 3: Batch load emails
            val emailCursor = context.contentResolver.query(
                ContactsContract.CommonDataKinds.Email.CONTENT_URI,
                arrayOf(
                    ContactsContract.CommonDataKinds.Email.CONTACT_ID,
                    ContactsContract.CommonDataKinds.Email.DATA
                ),
                null,
                null,
                null
            )

            emailCursor?.use { ec ->
                val contactIdIndex = ec.getColumnIndex(ContactsContract.CommonDataKinds.Email.CONTACT_ID)
                val emailIndex = ec.getColumnIndex(ContactsContract.CommonDataKinds.Email.DATA)

                while (ec.moveToNext()) {
                    val contactId = ec.getString(contactIdIndex)
                    val email = ec.getString(emailIndex)
                    if (!contactId.isNullOrBlank() && !email.isNullOrBlank()) {
                        val contact = contactsById[contactId]
                        if (contact != null && contact.email == null) {
                            contact.email = email
                        }
                    }
                }
            }

            // Step 4: Batch load names, company, job title
            val dataCursor = context.contentResolver.query(
                ContactsContract.Data.CONTENT_URI,
                arrayOf(
                    ContactsContract.Data.RAW_CONTACT_ID,
                    ContactsContract.Data.MIMETYPE,
                    ContactsContract.CommonDataKinds.StructuredName.GIVEN_NAME,
                    ContactsContract.CommonDataKinds.StructuredName.FAMILY_NAME,
                    ContactsContract.CommonDataKinds.Organization.COMPANY,
                    ContactsContract.CommonDataKinds.Organization.TITLE,
                    ContactsContract.CommonDataKinds.StructuredPostal.FORMATTED_ADDRESS
                ),
                null,
                null,
                null
            )

            dataCursor?.use { dc ->
                val rawContactIdIndex = dc.getColumnIndex(ContactsContract.Data.RAW_CONTACT_ID)
                val mimetypeIndex = dc.getColumnIndex(ContactsContract.Data.MIMETYPE)
                val givenNameIndex = dc.getColumnIndex(ContactsContract.CommonDataKinds.StructuredName.GIVEN_NAME)
                val familyNameIndex = dc.getColumnIndex(ContactsContract.CommonDataKinds.StructuredName.FAMILY_NAME)
                val companyIndex = dc.getColumnIndex(ContactsContract.CommonDataKinds.Organization.COMPANY)
                val titleIndex = dc.getColumnIndex(ContactsContract.CommonDataKinds.Organization.TITLE)
                val addressIndex = dc.getColumnIndex(ContactsContract.CommonDataKinds.StructuredPostal.FORMATTED_ADDRESS)

                while (dc.moveToNext()) {
                    val contactId = dc.getString(rawContactIdIndex) ?: continue
                    val mimetype = dc.getString(mimetypeIndex)
                    val contact = contactsById[contactId] ?: continue

                    when (mimetype) {
                        ContactsContract.CommonDataKinds.StructuredName.CONTENT_ITEM_TYPE -> {
                            contact.firstName = dc.getString(givenNameIndex)
                            contact.lastName = dc.getString(familyNameIndex)
                        }
                        ContactsContract.CommonDataKinds.Organization.CONTENT_ITEM_TYPE -> {
                            if (contact.company == null) {
                                contact.company = dc.getString(companyIndex)
                                contact.jobTitle = dc.getString(titleIndex)
                            }
                        }
                        ContactsContract.CommonDataKinds.StructuredPostal.CONTENT_ITEM_TYPE -> {
                            if (contact.address == null) {
                                contact.address = dc.getString(addressIndex)
                            }
                        }
                    }
                }
            }

            // Step 5: Batch load groups
            val groupCursor = context.contentResolver.query(
                ContactsContract.Data.CONTENT_URI,
                arrayOf(
                    ContactsContract.Data.RAW_CONTACT_ID,
                    ContactsContract.CommonDataKinds.GroupMembership.GROUP_ROW_ID
                ),
                "${ContactsContract.Data.MIMETYPE} = ?",
                arrayOf(ContactsContract.CommonDataKinds.GroupMembership.CONTENT_ITEM_TYPE),
                null
            )

            val contactGroups = mutableMapOf<String, MutableList<Long>>()
            groupCursor?.use { gc ->
                val contactIdIndex = gc.getColumnIndex(ContactsContract.Data.RAW_CONTACT_ID)
                val groupIdIndex = gc.getColumnIndex(ContactsContract.CommonDataKinds.GroupMembership.GROUP_ROW_ID)

                while (gc.moveToNext()) {
                    val contactId = gc.getString(contactIdIndex) ?: continue
                    val groupId = gc.getLong(groupIdIndex)
                    if (!contactGroups.containsKey(contactId)) {
                        contactGroups[contactId] = mutableListOf()
                    }
                    contactGroups[contactId]?.add(groupId)
                }
            }

            // Resolve group IDs to names
            val groupIds = contactGroups.values.flatten().distinct()
            val groupNamesById = mutableMapOf<Long, String>()
            if (groupIds.isNotEmpty()) {
                val groupsQuery = context.contentResolver.query(
                    ContactsContract.Groups.CONTENT_URI,
                    arrayOf(ContactsContract.Groups._ID, ContactsContract.Groups.TITLE),
                    "${ContactsContract.Groups._ID} IN (${groupIds.joinToString(",") { "?" }})",
                    groupIds.map { it.toString() }.toTypedArray(),
                    null
                )

                groupsQuery?.use { gq ->
                    val gidIndex = gq.getColumnIndex(ContactsContract.Groups._ID)
                    val titleIndex = gq.getColumnIndex(ContactsContract.Groups.TITLE)
                    while (gq.moveToNext()) {
                        val gid = gq.getLong(gidIndex)
                        val title = gq.getString(titleIndex)
                        if (!title.isNullOrBlank()) {
                            groupNamesById[gid] = title
                        }
                    }
                }
            }

            // Assign groups to contacts
            contactGroups.forEach { (contactId, groupIdsForContact) ->
                val contact = contactsById[contactId]
                if (contact != null) {
                    val groups = groupIdsForContact.mapNotNull { groupNamesById[it] }
                    if (groups.isNotEmpty()) {
                        contact.groups = groups
                    }
                }
            }

            return contactsById.values.toList()

        } catch (e: Exception) {
            throw e
        } finally {
            cursor?.close()
        }
    }

    private fun getContactGroups(context: Context, contactId: String): List<String> {
        val groups = mutableListOf<String>()
        var cursor: Cursor? = null
        try {
            cursor = context.contentResolver.query(
                ContactsContract.Data.CONTENT_URI,
                arrayOf(
                    ContactsContract.Data.MIMETYPE,
                    ContactsContract.CommonDataKinds.GroupMembership.GROUP_ROW_ID
                ),
                "${ContactsContract.Data.MIMETYPE} = ? AND ${ContactsContract.Data.RAW_CONTACT_ID} = ?",
                arrayOf(ContactsContract.CommonDataKinds.GroupMembership.CONTENT_ITEM_TYPE, contactId),
                null
            )
            cursor?.use {
                val groupIdIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.GroupMembership.GROUP_ROW_ID)
                while (it.moveToNext()) {
                    val groupId = it.getLong(groupIdIndex)
                    val groupCursor = context.contentResolver.query(
                        ContactsContract.Groups.CONTENT_URI,
                        arrayOf(ContactsContract.Groups.TITLE),
                        "${ContactsContract.Groups._ID} = ?",
                        arrayOf(groupId.toString()),
                        null
                    )
                    groupCursor?.use { gc ->
                        if (gc.moveToFirst()) {
                            val groupName = gc.getString(gc.getColumnIndex(ContactsContract.Groups.TITLE))
                            if (!groupName.isNullOrBlank() && groupName !in groups) {
                                groups.add(groupName)
                            }
                        }
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            cursor?.close()
        }
        return groups
    }
}
