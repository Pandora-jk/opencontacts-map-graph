package com.opencontacts.androidecosystem.contacts

import androidx.lifecycle.ViewModel

class ContactMapViewModel : ViewModel() {
    private val _contacts = mutableListOf<ContactRecord>()
    val contacts: List<ContactRecord> get() = _contacts.toList()

    fun refreshContacts() {
        // TODO: Implement actual contact loading
        _contacts.clear()
        // Add sample data for testing
        _contacts.add(
            ContactRecord(
                id = "1",
                displayName = "Sample Contact",
                phone = "555-0100",
                email = "sample@example.com"
            )
        )
    }

    override fun onCleared() {
        super.onCleared()
        _contacts.clear()
    }
}
