package com.openclaw.androidecosystem.contacts.contactsui

import android.content.Context
import android.util.AttributeSet
import android.view.Gravity
import android.widget.LinearLayout
import android.widget.TextView
import androidx.core.content.ContextCompat
import com.openclaw.androidecosystem.contacts.R
import com.openclaw.androidecosystem.contacts.contactsdata.ContactEntity

class ContactListItem @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null
) : LinearLayout(context, attrs) {
    private val titleView = TextView(context)
    private val subtitleView = TextView(context)
    private val metaView = TextView(context)

    init {
        orientation = VERTICAL
        gravity = Gravity.CENTER_VERTICAL
        val padding = resources.getDimensionPixelSize(R.dimen.spacing_medium)
        setPadding(padding, padding, padding, padding)
        background = ContextCompat.getDrawable(context, R.drawable.bg_card_surface)

        titleView.setTextAppearance(com.google.android.material.R.style.TextAppearance_Material3_TitleMedium)
        subtitleView.setTextAppearance(com.google.android.material.R.style.TextAppearance_Material3_BodyMedium)
        metaView.setTextAppearance(com.google.android.material.R.style.TextAppearance_Material3_LabelMedium)
        subtitleView.alpha = 0.8f
        metaView.alpha = 0.7f

        addView(titleView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
        addView(subtitleView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
        addView(metaView, LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT))
    }

    fun bind(contact: ContactEntity, markerCount: Int) {
        titleView.text = contact.displayName
        subtitleView.text = listOfNotNull(contact.phone, contact.email).joinToString(" • ").ifBlank {
            resources.getString(R.string.no_contact_channels)
        }
        metaView.text = resources.getString(
            R.string.contact_meta_template,
            contact.connectionStrength,
            markerCount
        )
        contentDescription = resources.getString(R.string.contact_list_item_description, contact.displayName)
    }
}
