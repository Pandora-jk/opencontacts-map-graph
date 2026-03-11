package com.opencontacts.androidecosystem.contacts

data class ContactRecord(
    val id: String,
    val displayName: String? = null,
    val phone: String? = null,
    val email: String? = null,
    val photoUri: String? = null,
    val lastContacted: Long? = null,
    val connectionStrength: Int = 0,
)
