package com.opencontacts.androidecosystem.contacts

import java.util.Locale

class ContactMarkerInfoWindow {
    fun contentFor(marker: ContactMapMarker): MarkerInfoContent {
        val normalizedCategory = marker.category ?: "uncategorized"
        val distance = marker.distanceKm?.let { String.format(Locale.US, "%.1f km away", it) } ?: "Distance unavailable"

        return MarkerInfoContent(
            title = marker.title,
            subtitle = marker.subtitle.ifBlank { "No phone or email on file" },
            meta = "$normalizedCategory • strength ${marker.connectionStrength}",
            distance = distance,
            contentDescription = "Marker information for ${marker.title}",
        )
    }
}
