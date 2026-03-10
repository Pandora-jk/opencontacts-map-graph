package com.openclaw.androidecosystem.contacts.contactsdata

import android.content.Context
import android.provider.ContactsContract
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class AndroidSystemContactDataSource(
    private val context: Context
) : SystemContactDataSource {

    override suspend fun fetchContacts(): List<SystemContactRecord> = withContext(Dispatchers.IO) {
        val contacts = mutableListOf<SystemContactRecord>()
        val projection = arrayOf(
            ContactsContract.Contacts._ID,
            ContactsContract.Contacts.DISPLAY_NAME,
            ContactsContract.Contacts.PHOTO_URI,
            ContactsContract.Contacts.LAST_TIME_CONTACTED,
            ContactsContract.Contacts.TIMES_CONTACTED
        )
        context.contentResolver.query(
            ContactsContract.Contacts.CONTENT_URI,
            projection,
            null,
            null,
            "${ContactsContract.Contacts.DISPLAY_NAME} COLLATE NOCASE ASC"
        )?.use { cursor ->
            val idIndex = cursor.getColumnIndexOrThrow(ContactsContract.Contacts._ID)
            val nameIndex = cursor.getColumnIndexOrThrow(ContactsContract.Contacts.DISPLAY_NAME)
            val photoIndex = cursor.getColumnIndexOrThrow(ContactsContract.Contacts.PHOTO_URI)
            val lastContactedIndex =
                cursor.getColumnIndexOrThrow(ContactsContract.Contacts.LAST_TIME_CONTACTED)
            val timesContactedIndex =
                cursor.getColumnIndexOrThrow(ContactsContract.Contacts.TIMES_CONTACTED)

            while (cursor.moveToNext()) {
                val contactId = cursor.getLong(idIndex)
                contacts += SystemContactRecord(
                    displayName = cursor.getString(nameIndex),
                    phone = queryPhone(contactId),
                    email = queryEmail(contactId),
                    photoUri = cursor.getString(photoIndex),
                    lastContacted = cursor.getLong(lastContactedIndex).takeIf { it > 0L },
                    interactionCount = cursor.getInt(timesContactedIndex)
                )
            }
        }
        contacts
    }

    private fun queryPhone(contactId: Long): String? {
        context.contentResolver.query(
            ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
            arrayOf(ContactsContract.CommonDataKinds.Phone.NUMBER),
            "${ContactsContract.CommonDataKinds.Phone.CONTACT_ID} = ?",
            arrayOf(contactId.toString()),
            null
        )?.use { cursor ->
            if (cursor.moveToFirst()) {
                return cursor.getString(
                    cursor.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Phone.NUMBER)
                )
            }
        }
        return null
    }

    private fun queryEmail(contactId: Long): String? {
        context.contentResolver.query(
            ContactsContract.CommonDataKinds.Email.CONTENT_URI,
            arrayOf(ContactsContract.CommonDataKinds.Email.ADDRESS),
            "${ContactsContract.CommonDataKinds.Email.CONTACT_ID} = ?",
            arrayOf(contactId.toString()),
            null
        )?.use { cursor ->
            if (cursor.moveToFirst()) {
                return cursor.getString(
                    cursor.getColumnIndexOrThrow(ContactsContract.CommonDataKinds.Email.ADDRESS)
                )
            }
        }
        return null
    }
}
