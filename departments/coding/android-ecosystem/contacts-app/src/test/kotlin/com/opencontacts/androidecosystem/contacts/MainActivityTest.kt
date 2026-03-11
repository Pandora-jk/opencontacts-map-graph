package com.opencontacts.androidecosystem.contacts

import android.content.Context
import android.view.View
import androidx.test.core.app.ApplicationProvider
import com.openclaw.androidecosystem.contacts.R
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class MainActivityTest {

    @Test
    fun launcherIntentTargetsMainActivityClass() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        val launchIntent = context.packageManager.getLaunchIntentForPackage(context.packageName)

        assertNotNull(launchIntent)
        assertEquals(MainActivity::class.java.name, launchIntent!!.component?.className)
    }

    @Test
    fun mainActivityHasPublicNoArgConstructor() {
        val constructor = MainActivity::class.java.getDeclaredConstructor()

        assertNotNull(constructor)
        assertTrue(constructor.parameterTypes.isEmpty())
    }

    @Test
    fun onCreateCompletesWithoutCrash() {
        Robolectric.buildActivity(MainActivity::class.java)
            .setup()
            .get()
    }

    @Test
    fun setContentViewUsesContactsMapLayout() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .setup()
            .get()

        val contentView = shadowOf(activity).contentView

        assertNotNull(contentView)
        assertEquals("activity_contacts_map", activity.resources.getResourceEntryName(R.layout.activity_contacts_map))
        assertEquals(
            activity.findViewById<View>(android.R.id.content).getChildAt(0),
            contentView,
        )
    }

    @Test
    fun viewModelIsInitializedDuringOnCreate() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .setup()
            .get()

        val viewModel = activity.readPrivateField("viewModel")

        assertNotNull(viewModel)
        assertTrue(viewModel is ContactMapViewModel)
    }

    @Test
    fun uiComponentsAreBound() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .setup()
            .get()

        val binding = activity.readPrivateField("binding")
        val rootId = activity.resources.getIdentifier("main_activity_root", "id", activity.packageName)
        val statusId = activity.resources.getIdentifier("status_text", "id", activity.packageName)
        val refreshId = activity.resources.getIdentifier("refresh_button", "id", activity.packageName)
        val mapContainerId = activity.resources.getIdentifier("map_container", "id", activity.packageName)

        assertNotNull(binding)
        assertTrue(rootId != 0)
        assertTrue(statusId != 0)
        assertTrue(refreshId != 0)
        assertTrue(mapContainerId != 0)
        assertNotNull(activity.findViewById<View>(rootId))
        assertNotNull(activity.findViewById<View>(statusId))
        assertNotNull(activity.findViewById<View>(refreshId))
        assertNotNull(activity.findViewById<View>(mapContainerId))
        assertEquals(rootId, shadowOf(activity).contentView.id)
    }

    private fun Any.readPrivateField(name: String): Any? {
        val field = javaClass.getDeclaredField(name)
        field.isAccessible = true
        return field.get(this)
    }
}
