package com.opencontacts.androidecosystem.contacts

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView

class ContactListFragment(private val mode: ContactListMode) : Fragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_contact_list, container, false)
        val recyclerView = view.findViewById<RecyclerView>(R.id.recycler_view)
        val emptyText = view.findViewById<TextView>(R.id.empty_text)

        recyclerView.layoutManager = LinearLayoutManager(requireContext())

        // Sample data - will be replaced with real data from ViewModel
        val contacts = getSampleContacts()
        
        if (contacts.isEmpty()) {
            recyclerView.visibility = View.GONE
            emptyText.visibility = View.VISIBLE
        } else {
            recyclerView.visibility = View.VISIBLE
            emptyText.visibility = View.GONE
            recyclerView.adapter = ContactAdapter(contacts)
        }

        return view
    }

    private fun getSampleContacts(): List<ContactRecord> {
        // TODO: Replace with actual ViewModel data based on mode
        return when (mode) {
            ContactListMode.ALL -> listOf(
                ContactRecord("1", "John Doe", phoneNumbers = listOf("555-0100")),
                ContactRecord("2", "Jane Smith", phoneNumbers = listOf("555-0101"))
            )
            ContactListMode.FAVORITES -> listOf(
                ContactRecord("1", "John Doe", phoneNumbers = listOf("555-0100"), isFavorite = true)
            )
            ContactListMode.GROUPS -> emptyList() // Will be implemented with groups
        }
    }
}
