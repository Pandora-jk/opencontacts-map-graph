package com.openclaw.androidecosystem.contacts.contactsui

import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity

data class ContactListRow(
    val contact: ContactEntity,
    val markerCount: Int
)

class ContactsAdapter : ListAdapter<ContactListRow, ContactsAdapter.ContactViewHolder>(DiffCallback) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ContactViewHolder {
        return ContactViewHolder(ContactListItem(parent.context))
    }

    override fun onBindViewHolder(holder: ContactViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ContactViewHolder(
        private val item: ContactListItem
    ) : RecyclerView.ViewHolder(item) {
        fun bind(row: ContactListRow) {
            item.bind(row.contact, row.markerCount)
        }
    }

    private object DiffCallback : DiffUtil.ItemCallback<ContactListRow>() {
        override fun areItemsTheSame(oldItem: ContactListRow, newItem: ContactListRow): Boolean {
            return oldItem.contact.id == newItem.contact.id
        }

        override fun areContentsTheSame(oldItem: ContactListRow, newItem: ContactListRow): Boolean {
            return oldItem == newItem
        }
    }
}
