package com.opencontacts.androidecosystem.contacts

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.appbar.MaterialToolbar

/**
 * Activity showing contacts filtered by group.
 * Opens as full-screen Activity to avoid overlay issues.
 */
class GroupContactsActivity : AppCompatActivity() {

    private lateinit var viewModel: ContactMapViewModel
    private var groupName: String? = null
    private val contactAdapter = ContactAdapter { contact ->
        // Open contact details
        val intent = ContactDetailsActivity.createIntent(this, contact)
        startActivity(intent)
    }
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            loadContacts()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_group_contacts)

        val toolbar = findViewById<MaterialToolbar>(R.id.toolbar)
        setSupportActionBar(toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        toolbar.setNavigationOnClickListener { finish() }

        groupName = intent.getStringExtra(EXTRA_GROUP_NAME)
        toolbar.title = groupName ?: "Group Contacts"

        val recyclerView = findViewById<RecyclerView>(R.id.recycler_view)

        recyclerView.layoutManager = LinearLayoutManager(this)
        recyclerView.adapter = contactAdapter

        viewModel = ViewModelProvider(this)[ContactMapViewModel::class.java]

        checkPermissionAndLoad()
    }

    private fun checkPermissionAndLoad() {
        val permission = Manifest.permission.READ_CONTACTS
        when {
            ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED -> {
                loadContacts()
            }
            else -> {
                requestPermissionLauncher.launch(permission)
            }
        }
    }

    private fun loadContacts() {
        viewModel.loadContacts(this)
        
        viewModel.contacts.observe(this) { allContacts ->
            val filtered = if (groupName != null) {
                allContacts.filter { it.groups.contains(groupName) }
            } else {
                allContacts
            }
            
            (contactAdapter as? ContactAdapter)?.submitContactList(filtered)
            
            val emptyText = findViewById<TextView>(R.id.empty_text)
            val recyclerView = findViewById<RecyclerView>(R.id.recycler_view)
            
            if (filtered.isEmpty()) {
                emptyText.visibility = View.VISIBLE
                recyclerView.visibility = View.GONE
                emptyText.text = "No contacts in '$groupName'"
            } else {
                emptyText.visibility = View.GONE
                recyclerView.visibility = View.VISIBLE
            }
        }
    }

    companion object {
        const val EXTRA_GROUP_NAME = "group_name"

        fun createIntent(context: Context, groupName: String) = 
            android.content.Intent(context, GroupContactsActivity::class.java).apply {
                putExtra(EXTRA_GROUP_NAME, groupName)
            }
    }
}
