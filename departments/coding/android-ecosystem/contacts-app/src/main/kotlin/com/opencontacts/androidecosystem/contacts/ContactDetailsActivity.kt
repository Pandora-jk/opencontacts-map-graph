package com.opencontacts.androidecosystem.contacts

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.card.MaterialCardView
import com.google.android.material.button.MaterialButton

/**
 * Full-screen contact details view.
 * Shows contact info with action buttons (call, message, etc.)
 */
class ContactDetailsActivity : AppCompatActivity() {

    private var contact: ContactRecord? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_contact_details)

        val toolbar = findViewById<MaterialToolbar>(R.id.toolbar)
        setSupportActionBar(toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        toolbar.setNavigationOnClickListener { finish() }

        // Get contact data from intent
        val contactId = intent.getStringExtra(EXTRA_CONTACT_ID)
        val contactName = intent.getStringExtra(EXTRA_CONTACT_NAME)
        val contactPhone = intent.getStringExtra(EXTRA_CONTACT_PHONE)
        val isFavorite = intent.getBooleanExtra(EXTRA_IS_FAVORITE, false)
        val contactGroups = intent.getStringArrayListExtra(EXTRA_CONTACT_GROUPS)

        if (contactId == null) {
            finish()
            return
        }

        contact = ContactRecord(
            id = contactId,
            displayName = contactName,
            phoneNumbers = listOfNotNull(contactPhone),
            isFavorite = isFavorite,
            groups = contactGroups ?: emptyList()
        )

        // Set up UI
        findViewById<TextView>(R.id.contact_name).text = contactName ?: "Unknown"
        findViewById<TextView>(R.id.contact_phone).text = contactPhone ?: "No phone number"

        // Groups chip
        val groupsText = findViewById<TextView>(R.id.contact_groups)
        if (contactGroups != null && contactGroups.isNotEmpty()) {
            groupsText.text = "Groups: ${contactGroups.joinToString(", ")}"
            groupsText.visibility = View.VISIBLE
        } else {
            groupsText.visibility = View.GONE
        }

        // Favorite badge
        val favoriteBadge = findViewById<TextView>(R.id.favorite_badge)
        if (isFavorite) {
            favoriteBadge.text = "★ Favorite"
            favoriteBadge.visibility = View.VISIBLE
        } else {
            favoriteBadge.visibility = View.GONE
        }

        // Call button
        findViewById<MaterialButton>(R.id.btn_call).setOnClickListener {
            contactPhone?.let { phone ->
                val intent = Intent(Intent.ACTION_DIAL).apply {
                    data = Uri.parse("tel:$phone")
                }
                startActivity(intent)
            }
        }

        // Message button
        findViewById<MaterialButton>(R.id.btn_message).setOnClickListener {
            contactPhone?.let { phone ->
                val intent = Intent(Intent.ACTION_SENDTO).apply {
                    data = Uri.parse("smsto:${Uri.encode(phone)}")
                }
                startActivity(intent)
            }
        }
    }

    companion object {
        const val EXTRA_CONTACT_ID = "contact_id"
        const val EXTRA_CONTACT_NAME = "contact_name"
        const val EXTRA_CONTACT_PHONE = "contact_phone"
        const val EXTRA_IS_FAVORITE = "is_favorite"
        const val EXTRA_CONTACT_GROUPS = "contact_groups"

        fun createIntent(contact: ContactRecord): Intent {
            return Intent().apply {
                putExtra(EXTRA_CONTACT_ID, contact.id)
                putExtra(EXTRA_CONTACT_NAME, contact.displayName)
                putExtra(EXTRA_CONTACT_PHONE, contact.phoneNumbers.firstOrNull())
                putExtra(EXTRA_IS_FAVORITE, contact.isFavorite)
                putStringArrayListExtra(EXTRA_CONTACT_GROUPS, ArrayList(contact.groups))
            }
        }
    }
}
