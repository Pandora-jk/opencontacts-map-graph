package com.openclaw.androidecosystem.contacts.contactsmap

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity
import com.openclaw.androidecosystem.contacts.contactsdata.ContactRepository
import com.openclaw.androidecosystem.contacts.contactsdata.ContactSyncResult
import com.openclaw.androidecosystem.contacts.contactsdata.ContactSyncStatus
import com.openclaw.androidecosystem.contacts.contactsgraph.ConnectionGraph
import com.openclaw.androidecosystem.contacts.contactsgraph.GraphAlgorithm
import com.openclaw.androidecosystem.contacts.contactssearch.ContactSearchFilter
import com.openclaw.androidecosystem.contacts.contactssearch.ContactSuggestion
import com.openclaw.androidecosystem.contacts.contactssearch.ContactSuggestionEngine
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

data class ContactMapMarker(
    val contactId: Long,
    val title: String,
    val subtitle: String,
    val coordinate: GeoCoordinate,
    val category: LocationCategory,
    val connectionStrength: Int
)

data class ContactMapUiState(
    val isSyncing: Boolean = false,
    val permissionRequired: Boolean = false,
    val searchQuery: String = "",
    val minimumConnectionStrength: Int = 0,
    val maxDistanceKm: Double? = null,
    val selectedCategories: Set<LocationCategory> = emptySet(),
    val contacts: List<ContactEntity> = emptyList(),
    val markers: List<ContactMapMarker> = emptyList(),
    val suggestions: List<ContactSuggestion> = emptyList(),
    val graph: ConnectionGraph = ConnectionGraph(emptyMap(), emptyList()),
    val syncResult: ContactSyncResult? = null
)

class ContactMapViewModel(
    private val contactRepository: ContactRepository,
    private val locationRepository: ContactLocationRepository,
    private val searchFilter: ContactSearchFilter = ContactSearchFilter(),
    private val suggestionEngine: ContactSuggestionEngine = ContactSuggestionEngine(),
    private val graphAlgorithm: GraphAlgorithm = GraphAlgorithm(),
    private val dispatcher: CoroutineDispatcher = Dispatchers.Default
) : ViewModel() {

    private val searchQuery = MutableStateFlow("")
    private val minimumConnectionStrength = MutableStateFlow(0)
    private val maxDistanceKm = MutableStateFlow<Double?>(null)
    private val selectedCategories = MutableStateFlow<Set<LocationCategory>>(emptySet())
    private val anchor = MutableStateFlow(DEFAULT_ANCHOR)
    private val isSyncing = MutableStateFlow(false)
    private val syncResult = MutableStateFlow<ContactSyncResult?>(null)

    val uiState: StateFlow<ContactMapUiState> = combine(
        contactRepository.observeContacts(),
        locationRepository.observeLocations(),
        searchQuery,
        minimumConnectionStrength,
        maxDistanceKm,
        selectedCategories,
        anchor,
        isSyncing,
        syncResult
    ) { contacts, locations, query, minStrength, distanceKm, categories, currentAnchor, syncing, lastSync ->
        val filteredContacts = searchFilter.filterContacts(
            contacts = contacts,
            query = query,
            minimumConnectionStrength = minStrength,
            locations = locations,
            anchor = currentAnchor,
            maxDistanceKm = distanceKm,
            categories = categories
        )

        val graph = graphAlgorithm.inferGraph(contacts)
        val recentIds = contacts.sortedByDescending { it.lastContacted ?: 0L }.take(3).map(ContactEntity::id).toSet()
        val suggestions = suggestionEngine.suggestContacts(
            contacts = filteredContacts.ifEmpty { contacts },
            graph = graph,
            recentContactIds = recentIds
        )

        ContactMapUiState(
            isSyncing = syncing,
            permissionRequired = lastSync?.status == ContactSyncStatus.PERMISSION_DENIED,
            searchQuery = query,
            minimumConnectionStrength = minStrength,
            maxDistanceKm = distanceKm,
            selectedCategories = categories,
            contacts = filteredContacts,
            markers = filteredContacts.flatMap { contact ->
                locations.filter { it.contactId == contact.id }.map { location ->
                    ContactMapMarker(
                        contactId = contact.id,
                        title = contact.displayName,
                        subtitle = location.label,
                        coordinate = location.coordinate,
                        category = location.category,
                        connectionStrength = contact.connectionStrength
                    )
                }
            },
            suggestions = suggestions,
            graph = graph,
            syncResult = lastSync
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(stopTimeoutMillis = 5_000),
        initialValue = ContactMapUiState()
    )

    fun updateSearchQuery(query: String) {
        searchQuery.value = query
    }

    fun updateMinimumConnectionStrength(value: Int) {
        minimumConnectionStrength.value = value.coerceAtLeast(0)
    }

    fun updateDistanceFilter(distanceKm: Double?) {
        maxDistanceKm.value = distanceKm?.takeIf { it > 0.0 }
    }

    fun toggleCategory(category: LocationCategory) {
        selectedCategories.value = selectedCategories.value.toMutableSet().apply {
            if (contains(category)) remove(category) else add(category)
        }
    }

    fun clearCategories() {
        selectedCategories.value = emptySet()
    }

    fun updateAnchor(coordinate: GeoCoordinate) {
        anchor.value = coordinate
    }

    fun syncContacts() {
        viewModelScope.launch(dispatcher) {
            isSyncing.value = true
            syncResult.value = contactRepository.syncSystemContacts()
            isSyncing.value = false
        }
    }

    companion object {
        val DEFAULT_ANCHOR = GeoCoordinate(37.7749, -122.4194)
    }
}
