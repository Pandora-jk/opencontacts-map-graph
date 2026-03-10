package com.openclaw.androidecosystem.contacts.contactsmap

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.openclaw.androidecosystem.contacts.contactsdata.ContactRepository
import com.openclaw.androidecosystem.contacts.contactsgraph.GraphAlgorithm
import com.openclaw.androidecosystem.contacts.contactssearch.ContactSearchFilter
import com.openclaw.androidecosystem.contacts.contactssearch.ContactSuggestionEngine

class ContactMapViewModelFactory(
    private val contactRepository: ContactRepository,
    private val locationRepository: ContactLocationRepository
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>): T {
        if (modelClass.isAssignableFrom(ContactMapViewModel::class.java)) {
            @Suppress("UNCHECKED_CAST")
            return ContactMapViewModel(
                contactRepository = contactRepository,
                locationRepository = locationRepository,
                searchFilter = ContactSearchFilter(),
                suggestionEngine = ContactSuggestionEngine(),
                graphAlgorithm = GraphAlgorithm()
            ) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class: ${modelClass.name}")
    }
}
