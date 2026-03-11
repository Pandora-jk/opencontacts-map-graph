package com.opencontacts.androidecosystem.contacts

import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider

class MainActivity : AppCompatActivity() {
    private lateinit var viewModel: ContactMapViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_contacts_map)

        viewModel = ViewModelProvider(this)[ContactMapViewModel::class.java]

        // Initialize UI components
        val statusText = findViewById<TextView>(R.id.status_text)
        val refreshButton = findViewById<Button>(R.id.refresh_button)

        statusText.text = "Contacts App Ready"
        refreshButton.setOnClickListener {
            viewModel.refreshContacts()
            statusText.text = "Contacts refreshed: ${viewModel.contacts.size} contacts"
        }

        // Load initial contacts
        viewModel.refreshContacts()
        statusText.text = "Loaded ${viewModel.contacts.size} contacts"
    }
}
