package com.opencontacts.mapgraph.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.opencontacts.mapgraph.data.local.entity.ContactEntity

@Composable
fun ContactListScreen() {
    val contacts = remember { listOf(
        ContactEntity(
            id = 1,
            displayName = "John Doe",
            phoneNumber = "+1-555-0123",
            email = "john.doe@example.com",
            addressCity = "Sydney",
            addressState = "NSW",
            addressCountry = "Australia",
            contactSource = "android"
        ),
        ContactEntity(
            id = 2,
            displayName = "Jane Smith",
            phoneNumber = "+61-412-345-678",
            email = "jane.smith@example.com",
            addressCity = "Melbourne",
            addressState = "VIC",
            addressCountry = "Australia",
            contactSource = "android"
        ),
        ContactEntity(
            id = 3,
            displayName = "Bob Johnson",
            phoneNumber = "+61-8-9000-0000",
            email = "bob.johnson@example.com",
            addressCity = "Perth",
            addressState = "WA",
            addressCountry = "Australia",
            contactSource = "android"
        )
    ) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "OpenContacts Map",
            style = MaterialTheme.typography.headlineMedium,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        if (contacts.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text("No contacts yet")
            }
        } else {
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(contacts) { contact ->
                    ContactListItem(contact = contact)
                }
            }
        }
    }
}

@Composable
fun ContactListItem(contact: ContactEntity) {
    Card(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = contact.displayName ?: "Unknown",
                style = MaterialTheme.typography.titleMedium
            )
            contact.phoneNumber?.let { phone ->
                Text(
                    text = phone,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            contact.email?.let { email ->
                Text(
                    text = email,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            if (!contact.addressCity.isNullOrBlank() || !contact.addressState.isNullOrBlank()) {
                Text(
                    text = "${contact.addressCity ?: ""} ${contact.addressState ?: ""}".trim(),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}
