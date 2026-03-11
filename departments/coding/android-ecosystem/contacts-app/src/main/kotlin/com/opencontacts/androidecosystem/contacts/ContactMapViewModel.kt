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

            cursor?.use {
                val idIndex = it.getColumnIndex(ContactsContract.Contacts._ID)
                val nameIndex = it.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME)
                val hasPhoneIndex = it.getColumnIndex(ContactsContract.Contacts.HAS_PHONE_NUMBER)

                while (it.moveToNext()) {
                    val id = it.getString(idIndex)
                    val name = it.getString(nameIndex)
                    val hasPhone = it.getInt(hasPhoneIndex)

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

                    contactList.add(
                        ContactRecord(
                            id = id,
                            displayName = name,
                            phoneNumbers = phoneNumbers
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
}
