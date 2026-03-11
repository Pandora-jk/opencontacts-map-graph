package com.opencontacts.androidecosystem.contacts

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import androidx.viewpager2.widget.ViewPager2
import com.google.android.material.bottomnavigation.BottomNavigationView

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

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

enum class ContactListMode { ALL, FAVORITES, GROUPS }
