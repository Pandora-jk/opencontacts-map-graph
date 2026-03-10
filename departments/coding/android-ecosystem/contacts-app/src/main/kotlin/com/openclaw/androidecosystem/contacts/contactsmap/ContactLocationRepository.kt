package com.openclaw.androidecosystem.contacts.contactsmap

import kotlinx.coroutines.flow.Flow

interface ContactLocationRepository {
    fun observeLocations(): Flow<List<ContactLocation>>
}
