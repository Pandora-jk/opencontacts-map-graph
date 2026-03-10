package com.opencontacts.androidecosystem.contacts.data

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(
    entities = [ContactEntity::class],
    version = 1,
    exportSchema = false,
)
abstract class ContactsDatabase : RoomDatabase() {
    abstract fun contactDao(): ContactDao
}
