package com.openclaw.androidecosystem.contacts.contactsdata

interface SystemContactDataSource {
    suspend fun fetchContacts(): List<SystemContactRecord>
}
