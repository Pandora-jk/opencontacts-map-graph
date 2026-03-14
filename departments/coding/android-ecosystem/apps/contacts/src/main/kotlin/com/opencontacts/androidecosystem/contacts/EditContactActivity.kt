package com.opencontacts.androidecosystem.contacts

import android.Manifest
import android.content.ContentValues
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.ContactsContract
import android.provider.ContactsContract.CommonDataKinds
import android.view.View
import android.widget.EditText
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.android.material.appbar.MaterialToolbar
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout

/**
 * Activity for editing or creating contacts.
 * Supports all standard Android contact fields.
 */
class EditContactActivity : AppCompatActivity() {

    private var contactId: String? = null
    private var isEditMode = false
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            loadContactData()
        } else {
            Toast.makeText(this, "Permission required to edit contacts", Toast.LENGTH_LONG).show()
            finish()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_edit_contact)

        val toolbar = findViewById<MaterialToolbar>(R.id.toolbar)
        setSupportActionBar(toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        toolbar.setNavigationOnClickListener { finish() }

        // Get contact ID from intent (if editing)
        contactId = intent.getStringExtra(EXTRA_CONTACT_ID)
        isEditMode = contactId != null

        toolbar.title = if (isEditMode) "Edit Contact" else "New Contact"

        // Save button
        findViewById<MaterialButton>(R.id.btn_save).setOnClickListener {
            saveContact()
        }

        // Cancel button
        findViewById<MaterialButton>(R.id.btn_cancel).setOnClickListener {
            finish()
        }

        // Check permission and load data
        checkPermissionAndLoad()
    }

    private fun checkPermissionAndLoad() {
        val permission = Manifest.permission.READ_CONTACTS
        when {
            ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED -> {
                loadContactData()
            }
            else -> {
                requestPermissionLauncher.launch(permission)
            }
        }
    }

    private fun loadContactData() {
        if (!isEditMode || contactId == null) return

        // Load existing contact data
        val cursor = contentResolver.query(
            ContactsContract.Contacts.CONTENT_URI,
            null,
            "${ContactsContract.Contacts._ID} = ?",
            arrayOf(contactId),
            null
        )

        cursor?.use {
            if (it.moveToFirst()) {
                val displayName = it.getString(it.getColumnIndex(ContactsContract.Contacts.DISPLAY_NAME))
                findViewById<TextInputEditText>(R.id.edit_first_name).setText(displayName)

                // Load phone numbers
                val phoneCursor = contentResolver.query(
                    CommonDataKinds.Phone.CONTENT_URI,
                    arrayOf(CommonDataKinds.Phone.NUMBER),
                    "${CommonDataKinds.Phone.CONTACT_ID} = ?",
                    arrayOf(contactId),
                    null
                )
                phoneCursor?.use { pc ->
                    if (pc.moveToFirst()) {
                        findViewById<TextInputEditText>(R.id.edit_phone).setText(pc.getString(0))
                    }
                }

                // Load email
                val emailCursor = contentResolver.query(
                    CommonDataKinds.Email.CONTENT_URI,
                    arrayOf(CommonDataKinds.Email.DATA),
                    "${CommonDataKinds.Email.CONTACT_ID} = ?",
                    arrayOf(contactId),
                    null
                )
                emailCursor?.use { ec ->
                    if (ec.moveToFirst()) {
                        findViewById<TextInputEditText>(R.id.edit_email).setText(ec.getString(0))
                    }
                }

                // Load company and title
                val orgCursor = contentResolver.query(
                    ContactsContract.Data.CONTENT_URI,
                    arrayOf(
                        CommonDataKinds.Organization.COMPANY,
                        CommonDataKinds.Organization.TITLE
                    ),
                    "${ContactsContract.Data.MIMETYPE} = ? AND ${ContactsContract.Data.RAW_CONTACT_ID} = ?",
                    arrayOf(CommonDataKinds.Organization.CONTENT_ITEM_TYPE, contactId),
                    null
                )
                orgCursor?.use { oc ->
                    if (oc.moveToFirst()) {
                        findViewById<TextInputEditText>(R.id.edit_company).setText(oc.getString(0))
                        findViewById<TextInputEditText>(R.id.edit_job_title).setText(oc.getString(1))
                    }
                }

                // Load address
                val addrCursor = contentResolver.query(
                    ContactsContract.Data.CONTENT_URI,
                    arrayOf(CommonDataKinds.StructuredPostal.FORMATTED_ADDRESS),
                    "${ContactsContract.Data.MIMETYPE} = ? AND ${ContactsContract.Data.RAW_CONTACT_ID} = ?",
                    arrayOf(CommonDataKinds.StructuredPostal.CONTENT_ITEM_TYPE, contactId),
                    null
                )
                addrCursor?.use { ac ->
                    if (ac.moveToFirst()) {
                        findViewById<TextInputEditText>(R.id.edit_address).setText(ac.getString(0))
                    }
                }
            }
        }
    }

    private fun saveContact() {
        val firstName = findViewById<TextInputEditText>(R.id.edit_first_name).text.toString().trim()
        val lastName = findViewById<TextInputEditText>(R.id.edit_last_name).text.toString().trim()
        val phone = findViewById<TextInputEditText>(R.id.edit_phone).text.toString().trim()
        val email = findViewById<TextInputEditText>(R.id.edit_email).text.toString().trim()
        val company = findViewById<TextInputEditText>(R.id.edit_company).text.toString().trim()
        val jobTitle = findViewById<TextInputEditText>(R.id.edit_job_title).text.toString().trim()
        val address = findViewById<TextInputEditText>(R.id.edit_address).text.toString().trim()

        if (firstName.isBlank() && lastName.isBlank()) {
            Toast.makeText(this, "At least a first or last name is required", Toast.LENGTH_SHORT).show()
            return
        }

        try {
            if (isEditMode && contactId != null) {
                updateExistingContact(firstName, lastName)
            } else {
                createNewContact(firstName, lastName, phone, email, company, jobTitle, address)
            }

            Toast.makeText(this, "Contact saved!", Toast.LENGTH_SHORT).show()
            finish()
        } catch (e: Exception) {
            Toast.makeText(this, "Error saving contact: ${e.message}", Toast.LENGTH_LONG).show()
            e.printStackTrace()
        }
    }

    private fun createNewContact(firstName: String, lastName: String, phone: String, email: String, company: String, jobTitle: String, address: String) {
        val rawContactValues = ContentValues().apply {
            putNull(ContactsContract.RawContacts.ACCOUNT_TYPE)
            putNull(ContactsContract.RawContacts.ACCOUNT_NAME)
        }
        val rawContactUri = contentResolver.insert(ContactsContract.RawContacts.CONTENT_URI, rawContactValues)
        val rawContactId: String? = rawContactUri?.lastPathSegment

        if (rawContactId != null) {
            // Add name
            val nameValues = ContentValues().apply {
                put(ContactsContract.Data.RAW_CONTACT_ID, rawContactId)
                put(ContactsContract.Data.MIMETYPE, CommonDataKinds.StructuredName.CONTENT_ITEM_TYPE)
                put(CommonDataKinds.StructuredName.GIVEN_NAME, firstName)
                put(CommonDataKinds.StructuredName.FAMILY_NAME, lastName)
            }
            contentResolver.insert(ContactsContract.Data.CONTENT_URI, nameValues)

            // Add phone
            if (phone.isNotBlank()) {
                val phoneValues = ContentValues()
                phoneValues.put(ContactsContract.Data.RAW_CONTACT_ID, rawContactId)
                phoneValues.put(ContactsContract.Data.MIMETYPE, CommonDataKinds.Phone.CONTENT_ITEM_TYPE)
                phoneValues.put(CommonDataKinds.Phone.NUMBER, phone)
                phoneValues.put(CommonDataKinds.Phone.TYPE, CommonDataKinds.Phone.TYPE_MOBILE)
                contentResolver.insert(ContactsContract.Data.CONTENT_URI, phoneValues)
            }

            // Add email
            if (email.isNotBlank()) {
                val emailValues = ContentValues()
                emailValues.put(ContactsContract.Data.RAW_CONTACT_ID, rawContactId)
                emailValues.put(ContactsContract.Data.MIMETYPE, CommonDataKinds.Email.CONTENT_ITEM_TYPE)
                emailValues.put(CommonDataKinds.Email.DATA, email)
                emailValues.put(CommonDataKinds.Email.TYPE, CommonDataKinds.Email.TYPE_HOME)
                contentResolver.insert(ContactsContract.Data.CONTENT_URI, emailValues)
            }

            // Add company and title
            if (company.isNotBlank() || jobTitle.isNotBlank()) {
                val orgValues = ContentValues()
                orgValues.put(ContactsContract.Data.RAW_CONTACT_ID, rawContactId)
                orgValues.put(ContactsContract.Data.MIMETYPE, CommonDataKinds.Organization.CONTENT_ITEM_TYPE)
                orgValues.put(CommonDataKinds.Organization.COMPANY, company)
                orgValues.put(CommonDataKinds.Organization.TITLE, jobTitle)
                contentResolver.insert(ContactsContract.Data.CONTENT_URI, orgValues)
            }

            // Add address
            if (address.isNotBlank()) {
                val addrValues = ContentValues()
                addrValues.put(ContactsContract.Data.RAW_CONTACT_ID, rawContactId)
                addrValues.put(ContactsContract.Data.MIMETYPE, CommonDataKinds.StructuredPostal.CONTENT_ITEM_TYPE)
                addrValues.put(CommonDataKinds.StructuredPostal.FORMATTED_ADDRESS, address)
                addrValues.put(CommonDataKinds.StructuredPostal.TYPE, CommonDataKinds.StructuredPostal.TYPE_HOME)
                contentResolver.insert(ContactsContract.Data.CONTENT_URI, addrValues)
            }
        }
    }

    private fun updateExistingContact(firstName: String, lastName: String) {
        val contactId = contactId ?: return

        // Update display name
        val nameValues = ContentValues().apply {
            put(CommonDataKinds.StructuredName.GIVEN_NAME, firstName)
            put(CommonDataKinds.StructuredName.FAMILY_NAME, lastName)
        }
        contentResolver.update(
            ContactsContract.Data.CONTENT_URI,
            nameValues,
            "${ContactsContract.Data.RAW_CONTACT_ID} = ? AND ${ContactsContract.Data.MIMETYPE} = ?",
            arrayOf(contactId, CommonDataKinds.StructuredName.CONTENT_ITEM_TYPE)
        )
    }

    companion object {
        const val EXTRA_CONTACT_ID = "contact_id"

        fun createIntent(context: android.content.Context, contactId: String? = null): Intent {
            return Intent(context, EditContactActivity::class.java).apply {
                putExtra(EXTRA_CONTACT_ID, contactId)
            }
        }
    }
}
