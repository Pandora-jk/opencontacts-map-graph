package com.openclaw.androidecosystem.contacts

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.widget.doAfterTextChanged
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.recyclerview.widget.LinearLayoutManager
import com.openclaw.androidecosystem.contacts.contactsmap.ContactMapUiState
import com.openclaw.androidecosystem.contacts.contactsmap.ContactMapViewModel
import com.openclaw.androidecosystem.contacts.contactsmap.ContactMapViewModelFactory
import com.openclaw.androidecosystem.contacts.contactsmap.LocationCategory
import com.openclaw.androidecosystem.contacts.contactsui.ContactListRow
import com.openclaw.androidecosystem.contacts.contactsui.ContactsAdapter
import com.openclaw.androidecosystem.contacts.contactsui.MarkerAdapter
import com.openclaw.androidecosystem.contacts.databinding.ActivityContactsMapBinding
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityContactsMapBinding

    private val viewModel: ContactMapViewModel by viewModels {
        ContactMapViewModelFactory(
            contactRepository = ContactsServiceLocator.provideRepository(this),
            locationRepository = ContactsServiceLocator.provideLocationRepository(this)
        )
    }

    private val contactsAdapter = ContactsAdapter()
    private val markerAdapter = MarkerAdapter()

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                viewModel.syncContacts()
            } else {
                viewModel.syncContacts()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityContactsMapBinding.inflate(layoutInflater)
        setContentView(binding.root)
        configureLists()
        configureInteractions()
        observeState()
    }

    private fun configureLists() {
        binding.contactsRecyclerView.layoutManager = LinearLayoutManager(this)
        binding.contactsRecyclerView.adapter = contactsAdapter

        binding.markerRecyclerView.layoutManager =
            LinearLayoutManager(this, LinearLayoutManager.HORIZONTAL, false)
        binding.markerRecyclerView.adapter = markerAdapter
    }

    private fun configureInteractions() {
        binding.searchInput.doAfterTextChanged { viewModel.updateSearchQuery(it?.toString().orEmpty()) }
        binding.syncButton.setOnClickListener { requestPermissionOrSync() }

        binding.connectionStrengthSeekBar.setOnSeekBarChangeListener(SimpleSeekBarChangeListener { progress ->
            viewModel.updateMinimumConnectionStrength(progress)
            binding.connectionStrengthValue.text = getString(R.string.connection_strength_value, progress)
        })

        binding.distanceAnyButton.setOnClickListener {
            viewModel.updateDistanceFilter(null)
        }
        binding.distanceLocalButton.setOnClickListener {
            viewModel.updateDistanceFilter(5.0)
        }
        binding.distanceRegionalButton.setOnClickListener {
            viewModel.updateDistanceFilter(25.0)
        }

        binding.homeFilterButton.setOnClickListener { viewModel.toggleCategory(LocationCategory.HOME) }
        binding.workFilterButton.setOnClickListener { viewModel.toggleCategory(LocationCategory.WORK) }
        binding.frequentFilterButton.setOnClickListener { viewModel.toggleCategory(LocationCategory.FREQUENT) }
        binding.clearFiltersButton.setOnClickListener {
            viewModel.clearCategories()
            viewModel.updateDistanceFilter(null)
            binding.connectionStrengthSeekBar.progress = 0
            binding.searchInput.setText("")
        }
    }

    private fun observeState() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect(::render)
            }
        }
    }

    private fun render(state: ContactMapUiState) {
        binding.statusText.text = when {
            state.isSyncing -> getString(R.string.syncing_contacts)
            state.permissionRequired -> getString(R.string.permission_required)
            state.syncResult != null -> getString(
                R.string.sync_status_template,
                state.syncResult.syncedCount,
                state.syncResult.skippedCount
            )
            else -> getString(R.string.ready_status)
        }

        binding.contactCountText.text = getString(R.string.contact_count_template, state.contacts.size)
        binding.suggestionsText.text = state.suggestions.joinToString(
            prefix = getString(R.string.suggestions_prefix),
            separator = " • "
        ) { suggestion -> suggestion.contact.displayName }
            .ifBlank { getString(R.string.suggestions_empty) }

        binding.emptyStateText.text =
            if (state.contacts.isEmpty()) getString(R.string.empty_contacts_state) else ""

        binding.homeFilterButton.isSelected = LocationCategory.HOME in state.selectedCategories
        binding.workFilterButton.isSelected = LocationCategory.WORK in state.selectedCategories
        binding.frequentFilterButton.isSelected = LocationCategory.FREQUENT in state.selectedCategories
        binding.distanceAnyButton.isSelected = state.maxDistanceKm == null
        binding.distanceLocalButton.isSelected = state.maxDistanceKm == 5.0
        binding.distanceRegionalButton.isSelected = state.maxDistanceKm == 25.0

        binding.graphView.setGraph(state.graph)
        markerAdapter.submitList(state.markers)
        contactsAdapter.submitList(
            state.contacts.map { contact ->
                ContactListRow(
                    contact = contact,
                    markerCount = state.markers.count { it.contactId == contact.id }
                )
            }
        )
    }

    private fun requestPermissionOrSync() {
        val permissionGranted = ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.READ_CONTACTS
        ) == PackageManager.PERMISSION_GRANTED
        if (permissionGranted) {
            viewModel.syncContacts()
        } else {
            permissionLauncher.launch(Manifest.permission.READ_CONTACTS)
        }
    }
}
