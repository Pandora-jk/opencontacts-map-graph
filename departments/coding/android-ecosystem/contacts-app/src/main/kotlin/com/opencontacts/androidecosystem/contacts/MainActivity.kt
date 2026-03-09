package com.opencontacts.androidecosystem.contacts

import android.app.Activity
import android.os.Bundle
import com.openclaw.androidecosystem.contacts.R

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_contacts_map)
    }
}
