package com.opencontacts.androidecosystem.contacts

import android.content.Context
import android.provider.ContactsContract
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import android.database.Cursor

class ContactMapViewModel : ViewModel() {

    private val _contacts = MutableLiveData<List<ContactRecord>>(emptyList())
    val contacts: LiveData<List<ContactRecord>> = _contacts

    fun loadContacts(context: Context) {
        // Only load if not already loaded
        if (_contacts.value?.isNotEmpty() == true) return

        val contactList = mutableListOf<ContactRecord>()
        var cursor: Cursor? = null
        
        try {
            cursor = context.contentResolver.query(
                ContactsContract.Contacts.CONTENT_URI,
                null,
                null,
                null,
                null
            )

            cursor?.use { contactsCursor ->
                val idIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts._ID)
                val nameIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
                val hasPhoneIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts.HAS_PHONE_NUMBER)
                val starredIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts.STARRED)
                val contactTypeIndex = contactsCursor.getColumnIndex(ContactsContract.Contacts.CONTACT_PRESENCE)

                while (contactsCursor.moveToNext()) {
                    val id = contactsCursor.getString(idIndex)
                    val name = contactsCursor.getString(nameIndex)
                    val hasPhone = contactsCursor.getInt(hasPhoneIndex)
                    val isStarred = contactsCursor.getInt(starredIndex) > 0

                    // Get phone numbers
                    val phoneNumbers = mutableListOf<String>()
                    if (hasPhone > 0) {
                        val phoneCursor = context.contentResolver.query(
                            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                            null,
                            "${ContactsContract.CommonDataKinds.Phone.CONTACT_ID} = ?",
                            arrayOf(id),
                            null
                        )
                        phoneCursor?.use { pc ->
                            val phoneIndex = pc.getColumnIndex(ContactsContract.CommonDataKinds.Phone.NUMBER)
                            while (pc.moveToNext()) {
                                phoneNumbers.add(pc.getString(phoneIndex))
                            }
                        }
                    }

                    // Get groups for this contact
                    val groups = getContactGroups(context, id)

                    contactList.add(
                        ContactRecord(
                            id = id,
                            displayName = name,
                            phoneNumbers = phoneNumbers,
                            isFavorite = isStarred,
                            groups = groups
                        )
                    )
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            cursor?.close()
        }

        _contacts.value = contactList
    }

    private fun getContactGroups(context: Context, contactId: String): List<String> {
        val groups = mutableListOf<String>()
        var cursor: Cursor? = null
        
        try {
            cursor = context.contentResolver.query(
                ContactsContract.Data.CONTENT_URI,
                arrayOf(ContactsContract.Data.MIMETYPE, ContactsContract.CommonDataKinds.GroupMembership.GROUP_ROW_ID),
                "${ContactsContract.Data.MIMETYPE} = ? AND ${ContactsContract.Data.RAW_CONTACT_ID} = ?",
                arrayOf(ContactsContract.CommonDataKinds.GroupMembership.CONTENT_ITEM_TYPE, contactId),
                null
            )

            cursor?.use {
                val groupIdIndex = it.getColumnIndex(ContactsContract.CommonDataKinds.GroupMembership.GROUP_ROW_ID)
                
                while (it.moveToNext()) {
                    val groupId = it.getLong(groupIdIndex)
                    
                    // Get group name by ID
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
