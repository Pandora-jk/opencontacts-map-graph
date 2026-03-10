package com.openclaw.androidecosystem.contacts.contactsdata

import android.Manifest
import android.content.Context
import androidx.core.content.ContextCompat
import android.content.pm.PackageManager

class AndroidContactsPermissionChecker(
    private val context: Context
) : ContactsPermissionChecker {
    override fun hasContactsPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.READ_CONTACTS
        ) == PackageManager.PERMISSION_GRANTED
    }
}
