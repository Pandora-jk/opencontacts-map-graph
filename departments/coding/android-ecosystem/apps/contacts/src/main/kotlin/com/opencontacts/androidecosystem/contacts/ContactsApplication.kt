package com.opencontacts.androidecosystem.contacts

import android.app.Application
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import com.google.android.material.color.DynamicColors

/**
 * Application class to enable Material You dynamic colors
 * This ensures the app uses the system theme and wallpaper colors on Android 12+
 */
class ContactsApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        // Enable dynamic colors (Material You) on supported devices
        // This will automatically adapt to system theme and wallpaper colors
        DynamicColors.applyToActivitiesIfAvailable(this)
    }
}
