package com.opencontacts.mapgraph.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.opencontacts.mapgraph.data.local.entity.ContactEntity
import com.opencontacts.mapgraph.ui.components.ContactListItem
import com.opencontacts.mapgraph.ui.components.NoContactsPlaceholder
import com.opencontacts.mapgraph.ui.components.ContactsLoading

@Composable
fun ContactListScreen(
    viewModel: ContactViewModel = viewModel()
) {
    val contacts by viewModel.contacts.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    val error by viewModel.error.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadContacts()
    }

    if (isLoading) {
        ContactsLoading()
    } else if (error != null) {
        ErrorScreen(error = error, onRetry = { viewModel.loadContacts() })
    } else if (contacts.isEmpty()) {
        NoContactsPlaceholder()
    } else {
        ContactList(contacts = contacts)
    }
}

@Composable
private fun ContactList(contacts: List<ContactEntity>) {
    val contactsOnMap = contacts.count { it.latitude != null && it.longitude != null }
    
    Column(modifier = Modifier.fillMaxSize()) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text("Contacts", style = MaterialTheme.typography.titleLarge)
                Text(
                    text = "$contactsOnMap/${contacts.size} with location",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(horizontal = 16.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            items(contacts, key = { it.id }) { contact ->
                ContactListItem(contact = contact)
            }
        }
    }
}

@Composable
private fun ErrorScreen(error: String, onRetry: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Error loading contacts",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.error
        )
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = error,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = onRetry) {
            Text("Retry")
        }
    }
}
