package com.openclaw.androidecosystem.contacts

import android.content.Context
import androidx.room.Room
import com.openclaw.androidecosystem.contacts.contactsdata.AndroidContactsPermissionChecker
import com.openclaw.androidecosystem.contacts.contactsdata.AndroidSystemContactDataSource
import com.openclaw.androidecosystem.contacts.contactsdata.ContactRepository
import com.openclaw.androidecosystem.contacts.contactsdata.ContactsDatabase
import com.openclaw.androidecosystem.contacts.contactsdata.DefaultContactRepository
import com.openclaw.androidecosystem.contacts.contactsmap.ContactLocationRepository
import com.openclaw.androidecosystem.contacts.contactsmap.DerivedContactLocationRepository

object ContactsServiceLocator {
    private var database: ContactsDatabase? = null
    private var repositoryOverride: ContactRepository? = null
    private var locationRepositoryOverride: ContactLocationRepository? = null

    fun provideRepository(context: Context): ContactRepository {
        return repositoryOverride ?: DefaultContactRepository(
            contactDao = provideDatabase(context).contactDao(),
            permissionChecker = AndroidContactsPermissionChecker(context),
            systemContactDataSource = AndroidSystemContactDataSource(context)
        )
    }

    fun provideLocationRepository(context: Context): ContactLocationRepository {
        return locationRepositoryOverride ?: DerivedContactLocationRepository(provideRepository(context).observeContacts())
    }

    fun replaceForTests(
        repository: ContactRepository,
        locationRepository: ContactLocationRepository
    ) {
        repositoryOverride = repository
        locationRepositoryOverride = locationRepository
    }

    fun reset() {
        repositoryOverride = null
        locationRepositoryOverride = null
        database = null
    }

    private fun provideDatabase(context: Context): ContactsDatabase {
        return database ?: Room.databaseBuilder(
            context.applicationContext,
            ContactsDatabase::class.java,
            "contacts-map.db"
        ).fallbackToDestructiveMigration().build().also { database = it }
    }
}
