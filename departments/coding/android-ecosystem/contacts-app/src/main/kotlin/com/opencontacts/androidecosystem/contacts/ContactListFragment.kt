package com.opencontacts.androidecosystem.contacts

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class ContactListFragment(
    private val mode: ContactListMode,
    private val groupName: String? = null
) : Fragment() {

    private lateinit var viewModel: ContactMapViewModel
    private val contactAdapter = ContactAdapter { contact ->
        // Open contact details in a new Activity
        val intent = ContactDetailsActivity.createIntent(contact)
        startActivity(intent)
    }
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            loadContacts()
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_contact_list, container, false)
        val recyclerView = view.findViewById<RecyclerView>(R.id.recycler_view)
        val emptyText = view.findViewById<TextView>(R.id.empty_text)

        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = contactAdapter

        viewModel = ViewModelProvider(requireActivity())[ContactMapViewModel::class.java]

        // Check permission and load contacts
        checkPermissionAndLoad()

        return view
    }

    private fun checkPermissionAndLoad() {
        val permission = Manifest.permission.READ_CONTACTS
        when {
            ContextCompat.checkSelfPermission(requireContext(), permission) == PackageManager.PERMISSION_GRANTED -> {
                loadContacts()
            }
            else -> {
                requestPermissionLauncher.launch(permission)
            }
        }
    }

    private fun loadContacts() {
        viewModel.loadContacts(requireContext())
        
        // Observe contacts based on mode
        viewModel.contacts.observe(viewLifecycleOwner) { allContacts ->
            val filtered = when (mode) {
                ContactListMode.ALL -> allContacts
                ContactListMode.FAVORITES -> allContacts.filter { it.isFavorite }
                ContactListMode.GROUPS -> {
                    // Filter by group name if specified
                    if (groupName != null) {
                        allContacts.filter { contact ->
                            contact.groups.contains(groupName)
                        }
                    } else {
                        allContacts
                    }
                }
            }
            
            contactAdapter.submitList(filtered)
            
            val emptyText = view?.findViewById<TextView>(R.id.empty_text)
            val recyclerView = view?.findViewById<RecyclerView>(R.id.recycler_view)
            
            if (filtered.isEmpty()) {
                emptyText?.visibility = View.VISIBLE
                recyclerView?.visibility = View.GONE
                emptyText?.text = when {
                    mode == ContactListMode.FAVORITES -> "No favorite contacts"
                    groupName != null -> "No contacts in '$groupName'"
                    else -> "No contacts"
                }
            } else {
                emptyText?.visibility = View.GONE
                recyclerView?.visibility = View.VISIBLE
            }
        }
    }
}

enum class ContactListMode { ALL, FAVORITES, GROUPS }
