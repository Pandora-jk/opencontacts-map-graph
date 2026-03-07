package com.opencontacts.mapgraph.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.opencontacts.mapgraph.ui.screens.ContactListScreen
import com.opencontacts.mapgraph.ui.theme.OpenContactsTheme

class MainActivity : ComponentActivity() {

    private val requiredPermissions = arrayOf(Manifest.permission.READ_CONTACTS)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val requestPermissionLauncher = registerForActivityResult(
            ActivityResultContracts.RequestMultiplePermissions()
        ) { permissions ->
            if (permissions.all { it.value }) {
                setContent {
                    OpenContactsTheme {
                        Surface(modifier = Modifier.fillMaxSize()) {
                            ContactListScreen()
                        }
                    }
                }
            } else {
                setContent {
                    OpenContactsTheme {
                        Surface(modifier = Modifier.fillMaxSize()) {
                            PermissionDeniedScreen()
                        }
                    }
                }
            }
        }

        val missingPermissions = requiredPermissions
            .filter { ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }
            .toTypedArray()

        if (missingPermissions.isEmpty()) {
            setContent {
                OpenContactsTheme {
                    Surface(modifier = Modifier.fillMaxSize()) {
                        ContactListScreen()
                    }
                }
            }
        } else {
            requestPermissionLauncher.launch(missingPermissions)
        }
    }

    @Composable
    private fun PermissionDeniedScreen() {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text(
                text = "Contacts Permission Required",
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "This app needs access to your contacts to display them.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
