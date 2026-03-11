package com.opencontacts.androidecosystem.contacts

import android.content.Context
import android.Manifest
import android.content.pm.PackageManager
import android.database.Cursor
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
    private val groupAdapter = GroupAdapter()
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
        
        val groups = mutableMapOf<String, Int>()
        var cursor: Cursor? = null
        
        try {
            // Query Android contact groups
            cursor = requireContext().contentResolver.query(
                ContactsContract.Groups.CONTENT_URI,
                arrayOf(
                    ContactsContract.Groups._ID,
                    ContactsContract.Groups.TITLE
                ),
                null,
                null,
                "${ContactsContract.Groups.TITLE} ASC"
            )

            cursor?.use { groupCursor ->
                val idIndex = groupCursor.getColumnIndex(ContactsContract.Groups._ID)
                val titleIndex = groupCursor.getColumnIndex(ContactsContract.Groups.TITLE)

                while (groupCursor.moveToNext()) {
                    val groupId = groupCursor.getString(idIndex)
                    val title = groupCursor.getString(titleIndex)
                    
                    if (!title.isNullOrBlank()) {
                        // Count contacts in this group
                        val contactCount = getGroupContactCount(requireContext(), groupId)
                        if (contactCount > 0) {
                            groups[title] = contactCount
                        }
                    }
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        } finally {
            cursor?.close()
        }

        val groupList = groups.map { (name, count) -> ContactGroup(name, count) }
        
        val emptyText = view?.findViewById<TextView>(R.id.empty_text)
        val recyclerView = view?.findViewById<RecyclerView>(R.id.recycler_view)
        
        if (groupList.isEmpty()) {
            emptyText?.visibility = View.VISIBLE
            emptyText?.text = "No contact groups found.\nGroups are created in your phone's Contacts app."
            recyclerView?.visibility = View.GONE
        } else {
            emptyText?.visibility = View.GONE
            recyclerView?.visibility = View.VISIBLE
            groupAdapter.submitList(groupList)
        }
    }

    private fun getGroupContactCount(context: Context, groupId: String): Int {
        var cursor: Cursor? = null
        try {
            cursor = context.contentResolver.query(
                ContactsContract.Data.CONTENT_URI,
                arrayOf(ContactsContract.Data.RAW_CONTACT_ID),
                "${ContactsContract.Data.MIMETYPE} = ? AND ${ContactsContract.CommonDataKinds.GroupMembership.GROUP_ROW_ID} = ?",
                arrayOf(ContactsContract.CommonDataKinds.GroupMembership.CONTENT_ITEM_TYPE, groupId),
                null
            )
            return cursor?.count ?: 0
        } catch (e: Exception) {
            return 0
        } finally {
            cursor?.close()
        }
    }
}

data class ContactGroup(val name: String, val count: Int)

class GroupAdapter : androidx.recyclerview.widget.ListAdapter<ContactGroup, GroupAdapter.GroupViewHolder>(GroupDiffCallback()) {

    class GroupViewHolder(itemView: View) : androidx.recyclerview.widget.RecyclerView.ViewHolder(itemView) {
        val groupName: TextView = itemView.findViewById(android.R.id.text1)
        val groupCount: TextView = itemView.findViewById(android.R.id.text2)
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
    }
}
