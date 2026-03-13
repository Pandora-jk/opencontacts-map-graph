package com.opencontacts.mapgraph.ui.components

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.opencontacts.mapgraph.data.local.entity.ContactEntity
import com.opencontacts.mapgraph.data.repository.ContactRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ContactViewModel(
    private val repository: ContactRepository = ContactRepository()
) : ViewModel() {

    private val _contacts = MutableStateFlow<List<ContactEntity>>(emptyList())
    val contacts: StateFlow<List<ContactEntity>> = _contacts.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    init {
        loadContacts()
    }

    private fun loadContacts() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                repository.getAllContacts().collect { contactList ->
                    _contacts.value = contactList
                }
            } catch (e: Exception) {
                // Handle error
                _contacts.value = emptyList()
            } finally {
                _isLoading.value = false
            }
        }
    }
}
