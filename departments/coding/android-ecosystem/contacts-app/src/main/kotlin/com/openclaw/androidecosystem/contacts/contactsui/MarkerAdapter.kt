package com.openclaw.androidecosystem.contacts.contactsui

import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.openclaw.androidecosystem.contacts.contactsmap.ContactMapMarker

class MarkerAdapter : ListAdapter<ContactMapMarker, MarkerAdapter.MarkerViewHolder>(DiffCallback) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MarkerViewHolder {
        return MarkerViewHolder(ContactMarkerInfoWindow(parent.context))
    }

    override fun onBindViewHolder(holder: MarkerViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class MarkerViewHolder(
        private val item: ContactMarkerInfoWindow
    ) : RecyclerView.ViewHolder(item) {
        fun bind(marker: ContactMapMarker) {
            item.bind(marker)
        }
    }

    private object DiffCallback : DiffUtil.ItemCallback<ContactMapMarker>() {
        override fun areItemsTheSame(oldItem: ContactMapMarker, newItem: ContactMapMarker): Boolean {
            return oldItem.contactId == newItem.contactId &&
                oldItem.coordinate == newItem.coordinate &&
                oldItem.category == newItem.category
        }

        override fun areContentsTheSame(oldItem: ContactMapMarker, newItem: ContactMapMarker): Boolean {
            return oldItem == newItem
        }
    }
}
