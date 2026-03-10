package com.openclaw.androidecosystem.contacts.contactsdata

data class SystemContactRecord(
    val displayName: String?,
    val phone: String?,
    val email: String?,
    val photoUri: String?,
    val lastContacted: Long?,
    val interactionCount: Int = 0
)
