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

/**
 * Fragment that displays contact groups (e.g., Family, Work, Friends).
 * Each group can be clicked to show contacts in that group.
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
        
        viewModel.contacts.observe(viewLifecycleOwner) { allContacts ->
            // Extract unique groups from contacts
            // For now, Android contacts don't have explicit groups in the simple query
            // We'll use a placeholder approach or extract from contact categories if available
            
            val groups = mutableMapOf<String, Int>()
            
            // For demonstration, we'll create groups based on contact name patterns
            // or use a default "All Contacts" group
            allContacts.forEach { contact ->
                // Simple heuristic: use first letter as a "group" for demo
                val firstLetter = contact.displayName?.firstOrNull()?.uppercase() ?: "#"
                groups[firstLetter] = groups.getOrDefault(firstLetter, 0) + 1
            }
            
            val groupList = groups.map { (name, count) -> ContactGroup(name, count) }
            groupAdapter.submitList(groupList)
            
            val emptyTextView = view?.findViewById<TextView>(R.id.empty_text)
            val recyclerView = view?.findViewById<RecyclerView>(R.id.recycler_view)
            
            if (groupList.isEmpty()) {
                emptyTextView?.visibility = View.VISIBLE
                recyclerView?.visibility = View.GONE
            } else {
                emptyTextView?.visibility = View.GONE
                recyclerView?.visibility = View.VISIBLE
            }
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
