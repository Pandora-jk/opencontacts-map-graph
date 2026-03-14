package com.opencontacts.androidecosystem.contacts

import android.content.res.Configuration
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible
import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import androidx.viewpager2.widget.ViewPager2
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.google.android.material.card.MaterialCardView
import com.google.android.material.color.MaterialColors

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        bindThemeVerificationCard()

        val bottomNavigation = findViewById<BottomNavigationView>(R.id.bottom_navigation)
        val viewPager = findViewById<ViewPager2>(R.id.view_pager)

        // Set up ViewPager with FragmentAdapter
        viewPager.adapter = ContactPagerAdapter(this)

        // Connect BottomNavigationView with ViewPager2
        bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_all -> {
                    viewPager.currentItem = 0
                    true
                }
                R.id.nav_favorites -> {
                    viewPager.currentItem = 1
                    true
                }
                R.id.nav_groups -> {
                    viewPager.currentItem = 2
                    true
                }
                R.id.nav_map -> {
                    viewPager.currentItem = 3
                    true
                }
                else -> false
            }
        }

        // Sync ViewPager with BottomNavigationView
        viewPager.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
            override fun onPageSelected(position: Int) {
                when (position) {
                    0 -> bottomNavigation.selectedItemId = R.id.nav_all
                    1 -> bottomNavigation.selectedItemId = R.id.nav_favorites
                    2 -> bottomNavigation.selectedItemId = R.id.nav_groups
                    3 -> bottomNavigation.selectedItemId = R.id.nav_map
                }
            }
        })
    }

    private fun bindThemeVerificationCard() {
        val card = findViewById<MaterialCardView>(R.id.theme_verification_card)
        val summaryView = findViewById<TextView>(R.id.theme_verification_summary)
        val hintView = findViewById<TextView>(R.id.theme_verification_hint)
        val rootView = findViewById<View>(android.R.id.content)
        val snapshot = ThemeVerificationSnapshot(
            dynamicColorCapable = Build.VERSION.SDK_INT >= Build.VERSION_CODES.S,
            darkThemeEnabled =
                (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) ==
                    Configuration.UI_MODE_NIGHT_YES,
            primaryColor = MaterialColors.getColor(rootView, com.google.android.material.R.attr.colorPrimary, 0),
            surfaceColor = MaterialColors.getColor(rootView, com.google.android.material.R.attr.colorSurface, 0),
        )

        summaryView.text = buildThemeVerificationSummary(snapshot)
        hintView.text = buildThemeVerificationHint(snapshot)
        card.isVisible = true
    }
}

// Simple FragmentStateAdapter for the 4 tabs
class ContactPagerAdapter(activity: AppCompatActivity) : FragmentStateAdapter(activity) {

    override fun getItemCount(): Int = 4

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> ContactListFragment(ContactListMode.ALL)
            1 -> ContactListFragment(ContactListMode.FAVORITES)
            2 -> ContactGroupsFragment()
            3 -> ContactMapFragment()
            else -> ContactListFragment(ContactListMode.ALL)
        }
    }
}
