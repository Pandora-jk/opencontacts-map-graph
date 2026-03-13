package com.opencontacts.androidecosystem.contacts.data

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "contacts",
    indices = [
        Index(value = ["displayName"]),
        Index(value = ["phone"]),
    ],
)
data class ContactEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val displayName: String,
    val phone: String? = null,
    val email: String? = null,
    val photoUri: String? = null,
    val lastContacted: Long? = null,
    val connectionStrength: Int = 0,
)
