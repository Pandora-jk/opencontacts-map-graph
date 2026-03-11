package com.opencontacts.androidecosystem.contacts

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.viewpager2.adapter.FragmentStateAdapter
import androidx.viewpager2.widget.ViewPager2
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator

class MainActivity : AppCompatActivity() {

    private val tabTitles = listOf("All", "Favorites", "Groups", "Map")

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val tabLayout = findViewById<TabLayout>(R.id.tab_layout)
        val viewPager = findViewById<ViewPager2>(R.id.view_pager)

        // Set up ViewPager with FragmentAdapter
        viewPager.adapter = ContactPagerAdapter(this)

        // Connect TabLayout with ViewPager2
        TabLayoutMediator(tabLayout, viewPager) { tab, position ->
            tab.text = tabTitles[position]
        }.attach()
    }
}

// Simple FragmentStateAdapter for the 4 tabs
class ContactPagerAdapter(activity: AppCompatActivity) : FragmentStateAdapter(activity) {

    override fun getItemCount(): Int = 4

    override fun createFragment(position: Int): androidx.fragment.app.Fragment {
        return when (position) {
            0 -> ContactListFragment(mode = ContactListMode.ALL)
            1 -> ContactListFragment(mode = ContactListMode.FAVORITES)
            2 -> ContactListFragment(mode = ContactListMode.GROUPS)
            3 -> ContactMapFragment()
            else -> ContactListFragment(mode = ContactListMode.ALL)
        }
    }
}

enum class ContactListMode { ALL, FAVORITES, GROUPS }
