package com.opencontacts.androidecosystem.contacts

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView

class ContactAdapter : ListAdapter<ContactRecord, ContactAdapter.ContactViewHolder>(ContactDiffCallback()) {

    class ContactViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val nameText: TextView = itemView.findViewById(android.R.id.text1)
        val phoneText: TextView = itemView.findViewById(android.R.id.text2)
    }

    class ContactDiffCallback : DiffUtil.ItemCallback<ContactRecord>() {
        override fun areItemsTheSame(oldItem: ContactRecord, newItem: ContactRecord): Boolean {
            return oldItem.id == newItem.id
        }

        override fun areContentsTheSame(oldItem: ContactRecord, newItem: ContactRecord): Boolean {
            return oldItem == newItem
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ContactViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(android.R.layout.simple_list_item_2, parent, false)
        return ContactViewHolder(view)
    }

    override fun onBindViewHolder(holder: ContactViewHolder, position: Int) {
        val contact = getItem(position)
        holder.nameText.text = contact.displayName ?: "Unknown"
        holder.phoneText.text = contact.phoneNumbers.firstOrNull() ?: ""
    }
}
