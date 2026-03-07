package com.opencontacts.mapgraph.ui.screens

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.opencontacts.mapgraph.OpenContactsApp
import com.opencontacts.mapgraph.data.local.entity.ContactEntity
import com.opencontacts.mapgraph.data.remote.NominatimApi
import com.opencontacts.mapgraph.data.repository.ContactRepository
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class ContactViewModel(application: Application) : AndroidViewModel(application) {

    private val repository: ContactRepository
    private val _contacts = MutableStateFlow<List<ContactEntity>>(emptyList())
    val contacts: StateFlow<List<ContactEntity>> = _contacts.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    init {
        val app = application as OpenContactsApp
        repository = ContactRepository(
            context = application,
            database = app.database,
            nominatimApi = NominatimApi()
        )
    }

    fun loadContacts() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            try {
                val result = repository.loadContactsFromSystem()
                result.fold(
                    onSuccess = {
                        repository.getAllContactsFlow().collect { contactList ->
                            _contacts.value = contactList
                            _isLoading.value = false
                            val pendingCount = repository.getGeocodingPendingCount()
                            if (pendingCount > 0) {
                                repository.geocodePendingContacts()
                            }
                        }
                    },
                    onFailure = { exception ->
                        _error.value = exception.message ?: "Unknown error"
                        _isLoading.value = false
                    }
                )
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load contacts"
                _isLoading.value = false
            }
        }
    }
}
