package com.opencontacts.androidecosystem.contacts

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.opencontacts.androidecosystem.contacts.databinding.ActivityContactsMapBinding

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityContactsMapBinding
    private lateinit var viewModel: ContactMapViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityContactsMapBinding.inflate(layoutInflater)
        setContentView(binding.root)

        viewModel = ViewModelProvider(this)[ContactMapViewModel::class.java]

        // Initialize UI components
        binding.statusText.text = "Contacts App Ready"
        binding.refreshButton.setOnClickListener {
            viewModel.refreshContacts()
        }
    }
}
