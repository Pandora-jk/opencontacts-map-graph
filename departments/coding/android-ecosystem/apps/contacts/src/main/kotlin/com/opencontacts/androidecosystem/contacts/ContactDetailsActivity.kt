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
 * Only displays fields that have actual values.
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
            phoneNumbers = contactPhone?.let { mutableListOf(it) } ?: mutableListOf(),
            isFavorite = isFavorite,
            groups = contactGroups ?: emptyList(),
            email = contactEmail,
            company = contactCompany,
            jobTitle = contactJobTitle,
            address = contactAddress
        )

        // Set up UI - only show fields with values
        
        // Contact Name (always show)
        findViewById<TextView>(R.id.contact_name).text = contactName ?: "Unknown"
        
        // Full Name (only if different from display name and has value)
        val fullName = buildString {
            if (!contactFirstName.isNullOrBlank()) {
                append(contactFirstName)
            }
            if (!contactLastName.isNullOrBlank()) {
                if (isNotEmpty()) append(" ")
                append(contactLastName)
            }
        }
        setupTextView(R.id.contact_full_name, fullName, contactName)
        
        // Favorite badge (only if favorite)
        val favoriteBadge = findViewById<TextView>(R.id.favorite_badge)
        if (isFavorite) {
            favoriteBadge.text = "★ Favorite"
            favoriteBadge.visibility = View.VISIBLE
        } else {
            favoriteBadge.visibility = View.GONE
        }

        // Phone (only if has value)
        setupTextView(R.id.contact_phone, contactPhone, null)
        setupClickableField(R.id.contact_phone, contactPhone) {
            val intent = Intent(Intent.ACTION_DIAL).apply {
                data = Uri.parse("tel:$contactPhone")
            }
            startActivity(intent)
        }

        // Email (only if has value)
        setupTextView(R.id.contact_email, contactEmail, null)
        setupClickableField(R.id.contact_email, contactEmail) {
            contactEmail?.let { email ->
                val intent = Intent(Intent.ACTION_SENDTO).apply {
                    data = Uri.parse("mailto:$email")
                }
                startActivity(intent)
            }
        }

        // Company & Job Title (only if has value)
        val companyText = buildString {
            if (!contactJobTitle.isNullOrBlank()) {
                append(contactJobTitle)
            }
            if (!contactCompany.isNullOrBlank()) {
                if (isNotEmpty()) append(" at ")
                append(contactCompany)
            }
        }
        setupTextView(R.id.contact_company, companyText, null)

        // Address (only if has value)
        setupTextView(R.id.contact_address, contactAddress, null)
        setupClickableField(R.id.contact_address, contactAddress) {
            contactAddress?.let { addr ->
                val intent = Intent(Intent.ACTION_VIEW).apply {
                    data = Uri.parse("geo:0,0?q=${Uri.encode(addr)}")
                }
                startActivity(intent)
            }
        }

        // Groups (only if has value)
        val groupsContainer = findViewById<View>(R.id.contact_groups_container)
        val groupsTextView = findViewById<TextView>(R.id.contact_groups)
        if (contactGroups != null && contactGroups.isNotEmpty()) {
            groupsContainer.visibility = View.VISIBLE
            groupsTextView.text = contactGroups.joinToString(", ")
        } else {
            groupsContainer.visibility = View.GONE
        }

        // Call button (only if has phone)
        findViewById<MaterialButton>(R.id.btn_call).apply {
            if (contactPhone != null) {
                val phone = contactPhone
                visibility = View.VISIBLE
                setOnClickListener {
                    val intent = Intent(Intent.ACTION_DIAL).apply {
                        data = Uri.parse("tel:$phone")
                    }
                    startActivity(intent)
                }
            } else {
                visibility = View.GONE
            }
        }

        // Message button (only if has phone)
        findViewById<MaterialButton>(R.id.btn_message).apply {
            if (contactPhone != null) {
                val phone = contactPhone
                visibility = View.VISIBLE
                setOnClickListener {
                    val intent = Intent(Intent.ACTION_SENDTO).apply {
                        data = Uri.parse("smsto:${Uri.encode(phone)}")
                    }
                    startActivity(intent)
                }
            } else {
                visibility = View.GONE
            }
        }
    }
    
    /**
     * Sets text and visibility - only shows if value is not blank
     */
    private fun setupTextView(viewId: Int, value: String?, fallbackValue: String?) {
        val textView = findViewById<TextView>(viewId)
        val displayValue = value?.takeIf { it.isNotBlank() } ?: fallbackValue
        if (!displayValue.isNullOrBlank()) {
            textView.text = displayValue
            textView.visibility = View.VISIBLE
        } else {
            textView.visibility = View.GONE
        }
    }
    
    /**
     * Makes a field clickable only if it has a value
     */
    private fun setupClickableField(viewId: Int, value: String?, onClick: () -> Unit) {
        val textView = findViewById<TextView>(viewId)
        if (!value.isNullOrBlank()) {
            textView.setOnClickListener { onClick() }
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
