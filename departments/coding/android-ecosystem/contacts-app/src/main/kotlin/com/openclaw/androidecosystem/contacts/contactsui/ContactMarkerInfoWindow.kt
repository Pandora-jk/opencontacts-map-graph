package com.openclaw.androidecosystem.contacts.contactsui

import android.content.Context
import android.util.AttributeSet
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.ContextCompat
import com.openclaw.androidecosystem.contacts.R
import com.openclaw.androidecosystem.contacts.contactsmap.ContactMapMarker

class ContactMarkerInfoWindow @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : LinearLayout(context, attrs) {
    private val titleView = TextView(context)
    private val subtitleView = TextView(context)
    private val strengthView = TextView(context)

    init {
        orientation = VERTICAL
        gravity = Gravity.CENTER_VERTICAL
        val padding = resources.getDimensionPixelSize(R.dimen.spacing_medium)
        setPadding(padding, padding, padding, padding)
        background = ContextCompat.getDrawable(context, R.drawable.bg_marker_surface)

        titleView.setTextAppearance(com.google.android.material.R.style.TextAppearance_Material3_TitleSmall)
        subtitleView.setTextAppearance(com.google.android.material.R.style.TextAppearance_Material3_BodySmall)
        strengthView.setTextAppearance(com.google.android.material.R.style.TextAppearance_Material3_LabelMedium)

        addView(titleView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
        addView(subtitleView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
        addView(strengthView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
    }

    fun bind(marker: ContactMapMarker) {
        titleView.text = marker.title
        subtitleView.text = marker.subtitle
        strengthView.text = resources.getString(
            R.string.marker_strength_template,
            marker.category.name.lowercase().replaceFirstChar(Char::titlecase),
            marker.connectionStrength
        )
        contentDescription = resources.getString(R.string.marker_info_description, marker.title)
    }
}
