package com.opencontacts.mapgraph

import android.app.Application
import com.opencontacts.mapgraph.data.local.ContactDatabase

class OpenContactsApp : Application() {
    
    val database: ContactDatabase by lazy {
        ContactDatabase.getDatabase(this)
    }
    
    override fun onCreate() {
        super.onCreate()
        // Initialize database on app start
        database
    }
}
