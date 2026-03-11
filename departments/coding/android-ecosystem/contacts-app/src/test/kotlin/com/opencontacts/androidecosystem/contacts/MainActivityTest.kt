package com.opencontacts.androidecosystem.contacts

import android.view.View
import org.junit.Assert.*
import org.junit.Test
import org.robolectric.Robolectric
import org.robolectric.Shadows.shadowOf

class MainActivityTest {
    @Test
    fun mainActivityCanBeInstantiated() {
        val activity = Robolectric.buildActivity(MainActivity::class.java).create().get()
        assertNotNull(activity)
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
            .create()
            .get()
    }

    @Test
    fun setContentViewIsCalled() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .create()
            .get()

        val contentView = shadowOf(activity).contentView
        assertNotNull(contentView)
    }

    @Test
    fun viewModelIsInitializedDuringOnCreate() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .create()
            .get()

        val viewModel = activity.readPrivateField("viewModel")

        assertNotNull(viewModel)
        assertTrue(viewModel is ContactMapViewModel)
    }

    @Test
    fun uiComponentsAreBound() {
        val activity = Robolectric.buildActivity(MainActivity::class.java)
            .create()
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
