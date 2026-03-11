package com.opencontacts.androidecosystem.contacts

import android.Manifest
import android.content.Context
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
import com.google.android.material.chip.Chip

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
        val contactEmail = intent.getStringExtra(EXTRA_CONTACT_EMAIL)
        val contactCompany = intent.getStringExtra(EXTRA_CONTACT_COMPANY)
        val contactJobTitle = intent.getStringExtra(EXTRA_CONTACT_JOB_TITLE)
        val contactAddress = intent.getStringExtra(EXTRA_CONTACT_ADDRESS)
        val contactFirstName = intent.getStringExtra(EXTRA_CONTACT_FIRST_NAME)
        val contactLastName = intent.getStringExtra(EXTRA_CONTACT_LAST_NAME)

        if (contactId == null) {
            finish()
            return
        }

        contact = ContactRecord(
            id = contactId,
            displayName = contactName,
            firstName = contactFirstName,
            lastName = contactLastName,
            phoneNumbers = listOfNotNull(contactPhone),
            isFavorite = isFavorite,
            groups = contactGroups ?: emptyList(),
            email = contactEmail,
            company = contactCompany,
            jobTitle = contactJobTitle,
            address = contactAddress
        )

        // Set up UI
        findViewById<TextView>(R.id.contact_name).text = contactName ?: "Unknown"
        
        // Show first/last name if available
        val fullName = buildString {
            if (!contactFirstName.isNullOrBlank()) {
                append(contactFirstName)
            }
            if (!contactLastName.isNullOrBlank()) {
                if (isNotEmpty()) append(" ")
                append(contactLastName)
            }
        }
        if (fullName.isNotBlank()) {
            findViewById<TextView>(R.id.contact_full_name).apply {
                text = fullName
                visibility = View.VISIBLE
            }
        }

        // Phone
        findViewById<TextView>(R.id.contact_phone).apply {
            text = contactPhone ?: "No phone number"
            visibility = if (contactPhone != null) View.VISIBLE else View.GONE
        }

        // Email
        findViewById<TextView>(R.id.contact_email).apply {
            text = contactEmail
            visibility = if (!contactEmail.isNullOrBlank()) View.VISIBLE else View.GONE
            setOnClickListener {
                contactEmail?.let { email ->
                    val intent = Intent(Intent.ACTION_SENDTO).apply {
                        data = Uri.parse("mailto:$email")
                    }
                    startActivity(intent)
                }
            }
        }

        // Company & Job Title
        findViewById<TextView>(R.id.contact_company).apply {
            val companyText = buildString {
                if (!contactJobTitle.isNullOrBlank()) {
                    append(contactJobTitle)
                }
                if (!contactCompany.isNullOrBlank()) {
                    if (isNotEmpty()) append(" at ")
                    append(contactCompany)
                }
            }
            text = companyText
            visibility = if (companyText.isNotBlank()) View.VISIBLE else View.GONE
        }

        // Address
        findViewById<TextView>(R.id.contact_address).apply {
            text = contactAddress
            visibility = if (!contactAddress.isNullOrBlank()) View.VISIBLE else View.GONE
            setOnClickListener {
                contactAddress?.let { addr ->
                    val intent = Intent(Intent.ACTION_VIEW).apply {
                        data = Uri.parse("geo:0,0?q=${Uri.encode(addr)}")
                    }
                    startActivity(intent)
                }
            }
        }

        // Groups chip
        val groupsContainer = findViewById<View>(R.id.contact_groups_container)
        if (contactGroups != null && contactGroups.isNotEmpty()) {
            groupsContainer.visibility = View.VISIBLE
            // Groups will be displayed as chips
        } else {
            groupsContainer.visibility = View.GONE
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
        const val EXTRA_CONTACT_EMAIL = "contact_email"
        const val EXTRA_CONTACT_COMPANY = "contact_company"
        const val EXTRA_CONTACT_JOB_TITLE = "contact_job_title"
        const val EXTRA_CONTACT_ADDRESS = "contact_address"
        const val EXTRA_CONTACT_FIRST_NAME = "contact_first_name"
        const val EXTRA_CONTACT_LAST_NAME = "contact_last_name"
        const val EXTRA_IS_FAVORITE = "is_favorite"
        const val EXTRA_CONTACT_GROUPS = "contact_groups"

        fun createIntent(context: Context, contact: ContactRecord): Intent {
            return Intent(context, ContactDetailsActivity::class.java).apply {
                putExtra(EXTRA_CONTACT_ID, contact.id)
                putExtra(EXTRA_CONTACT_NAME, contact.displayName)
                putExtra(EXTRA_CONTACT_PHONE, contact.phoneNumbers.firstOrNull())
                putExtra(EXTRA_CONTACT_EMAIL, contact.email)
                putExtra(EXTRA_CONTACT_COMPANY, contact.company)
                putExtra(EXTRA_CONTACT_JOB_TITLE, contact.jobTitle)
                putExtra(EXTRA_CONTACT_ADDRESS, contact.address)
                putExtra(EXTRA_CONTACT_FIRST_NAME, contact.firstName)
                putExtra(EXTRA_CONTACT_LAST_NAME, contact.lastName)
                putExtra(EXTRA_IS_FAVORITE, contact.isFavorite)
                putStringArrayListExtra(EXTRA_CONTACT_GROUPS, ArrayList(contact.groups))
            }
        }
    }
}
