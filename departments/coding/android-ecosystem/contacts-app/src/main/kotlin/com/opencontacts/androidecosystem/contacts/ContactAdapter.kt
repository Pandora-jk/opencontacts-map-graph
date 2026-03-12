package com.opencontacts.androidecosystem.contacts

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView

sealed class ContactListItem {
    data class ContactItem(val contact: ContactRecord) : ContactListItem()
    data class HeaderItem(val letter: String) : ContactListItem()
}

class ContactAdapter(
    private val onItemClick: ((ContactRecord) -> Unit)? = null
) : ListAdapter<ContactListItem, RecyclerView.ViewHolder>(ContactDiffCallback()) {

    companion object {
        const val TYPE_HEADER = 0
        const val TYPE_CONTACT = 1
    }

    class HeaderViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val headerText: TextView = itemView.findViewById(android.R.id.text1)
    }

    class ContactViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val nameText: TextView = itemView.findViewById(android.R.id.text1)
        val phoneText: TextView = itemView.findViewById(android.R.id.text2)
    }

    class ContactDiffCallback : DiffUtil.ItemCallback<ContactListItem>() {
        override fun areItemsTheSame(oldItem: ContactListItem, newItem: ContactListItem): Boolean {
            return when {
                oldItem is ContactListItem.ContactItem && newItem is ContactListItem.ContactItem -> 
                    oldItem.contact.id == newItem.contact.id
                oldItem is ContactListItem.HeaderItem && newItem is ContactListItem.HeaderItem -> 
                    oldItem.letter == newItem.letter
                else -> false
            }
        }

        override fun areContentsTheSame(oldItem: ContactListItem, newItem: ContactListItem): Boolean {
            return oldItem == newItem
        }
    }

    override fun getItemViewType(position: Int): Int {
        return when (getItem(position)) {
            is ContactListItem.HeaderItem -> TYPE_HEADER
            is ContactListItem.ContactItem -> TYPE_CONTACT
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_HEADER -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(android.R.layout.simple_list_item_1, parent, false)
                HeaderViewHolder(view)
            }
            TYPE_CONTACT -> {
                val view = LayoutInflater.from(parent.context)
                    .inflate(android.R.layout.simple_list_item_2, parent, false)
                ContactViewHolder(view)
            }
            else -> throw IllegalArgumentException("Unknown view type")
        }
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        val item = getItem(position)
        
        when (holder) {
            is HeaderViewHolder -> {
                if (item is ContactListItem.HeaderItem) {
                    holder.headerText.text = item.letter
                    // Make header more visible with styling
                    holder.headerText.setPadding(16, 32, 16, 8)
                    holder.headerText.textSize = 14f
                }
            }
            is ContactViewHolder -> {
                if (item is ContactListItem.ContactItem) {
                    val contact = item.contact
                    holder.nameText.text = contact.displayName ?: "Unknown"
                    holder.phoneText.text = contact.phoneNumbers.firstOrNull() ?: ""
                    
                    holder.itemView.setOnClickListener {
                        onItemClick?.invoke(contact)
                    }
                }
            }
        }
    }
    
    fun submitContactList(contacts: List<ContactRecord>) {
        val items = mutableListOf<ContactListItem>()
        val sortedContacts = contacts.sortedBy { it.displayName?.lowercase() }
        
        var currentLetter = ""
        
        sortedContacts.forEach { contact ->
            val letter = contact.displayName?.firstOrNull()?.toString()?.uppercase() ?: "#"
            
            if (letter != currentLetter) {
                items.add(ContactListItem.HeaderItem(letter))
                currentLetter = letter
            }
            
            items.add(ContactListItem.ContactItem(contact))
        }
        
        submitList(items)
    }
}
