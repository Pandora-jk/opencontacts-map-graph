package com.opencontacts.androidecosystem.contacts

import android.Manifest
import android.content.pm.PackageManager
import android.database.Cursor
import android.net.Uri
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
import android.provider.ContactsContract

/**
 * Fragment that displays actual Android contact groups.
 * Clicking a group shows contacts in that group.
 */
class ContactGroupsFragment : Fragment() {

    private lateinit var viewModel: ContactMapViewModel
    private val groupAdapter = GroupAdapter { group ->
        // Navigate to contacts filtered by this group
        val fragment = ContactListFragment(ContactListMode.ALL, groupName = group.name)
        parentFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .addToBackStack(null)
            .commit()
    }
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            loadGroups()
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        val view = inflater.inflate(R.layout.fragment_contact_groups, container, false)
        val recyclerView = view.findViewById<RecyclerView>(R.id.recycler_view)
        val emptyText = view.findViewById<TextView>(R.id.empty_text)

        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = groupAdapter

        viewModel = ViewModelProvider(requireActivity())[ContactMapViewModel::class.java]

        checkPermissionAndLoad()

        return view
    }

    private fun checkPermissionAndLoad() {
        val permission = Manifest.permission.READ_CONTACTS
        when {
            ContextCompat.checkSelfPermission(requireContext(), permission) == PackageManager.PERMISSION_GRANTED -> {
                loadGroups()
            }
            else -> {
                requestPermissionLauncher.launch(permission)
            }
        }
    }

    private fun loadGroups() {
        viewModel.loadContacts(requireContext())
        
        val groups = mutableListOf<ContactGroup>()
        var cursor: Cursor? = null
        
        try {
            // Query Android contact groups
            cursor = requireContext().contentResolver.query(
                ContactsContract.Groups.CONTENT_URI,
                arrayOf(
                    ContactsContract.Groups._ID,
                    ContactsContract.Groups.TITLE,
                    ContactsContract.Groups.COUNT
                ),
                null,
                null,
                "${ContactsContract.Groups.TITLE} ASC"
            )

            cursor?.use {
                val titleIndex = it.getColumnIndex(ContactsContract.Groups.TITLE)
                val countIndex = it.getColumnIndex(ContactsContract.Groups.COUNT)

                while (it.moveToNext()) {
                    val title = it.getString(titleIndex)
                    val count = it.getInt(countIndex)
                    
                    // Only show groups with contacts
                    if (!title.isNullOrBlank() && count > 0) {
                        groups.add(ContactGroup(title, count))
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            cursor?.close()
        }

        // If no groups found, show a message
        val emptyText = view?.findViewById<TextView>(R.id.empty_text)
        val recyclerView = view?.findViewById<RecyclerView>(R.id.recycler_view)
        
        if (groups.isEmpty()) {
            emptyText?.visibility = View.VISIBLE
            emptyText?.text = "No contact groups found.\nGroups are created in your phone's Contacts app."
            recyclerView?.visibility = View.GONE
        } else {
            emptyText?.visibility = View.GONE
            recyclerView?.visibility = View.VISIBLE
            groupAdapter.submitList(groups)
        }
    }
}

data class ContactGroup(val name: String, val count: Int)

class GroupAdapter(private val onItemClick: (ContactGroup) -> Unit) : androidx.recyclerview.widget.ListAdapter<ContactGroup, GroupAdapter.GroupViewHolder>(GroupDiffCallback()) {

    class GroupViewHolder(itemView: View) : androidx.recyclerview.widget.RecyclerView.ViewHolder(itemView) {
        val groupName: TextView = itemView.findViewById(android.R.id.text1)
        val groupCount: TextView = itemView.findViewById(android.R.id.text2)
        
        init {
            itemView.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != androidx.recyclerview.widget.RecyclerView.NO_POSITION) {
                    val group = getItem(position)
                    // Pass group info to callback
                }
            }
        }
    }

    class GroupDiffCallback : androidx.recyclerview.widget.DiffUtil.ItemCallback<ContactGroup>() {
        override fun areItemsTheSame(oldItem: ContactGroup, newItem: ContactGroup): Boolean {
            return oldItem.name == newItem.name
        }

        override fun areContentsTheSame(oldItem: ContactGroup, newItem: ContactGroup): Boolean {
            return oldItem == newItem
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): GroupViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(android.R.layout.simple_list_item_2, parent, false)
        return GroupViewHolder(view)
    }

    override fun onBindViewHolder(holder: GroupViewHolder, position: Int) {
        val group = getItem(position)
        holder.groupName.text = group.name
        holder.groupCount.text = "${group.count} contacts"
        
        holder.itemView.setOnClickListener {
            onItemClick(group)
        }
    }
}
