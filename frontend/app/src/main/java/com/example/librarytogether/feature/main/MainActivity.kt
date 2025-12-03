package com.example.librarytogether.feature.main

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.navigation.NavOptions
import androidx.navigation.fragment.NavHostFragment
import androidx.navigation.ui.setupWithNavController
import com.example.librarytogether.R
import com.example.librarytogether.feature.library.LibraryFragment
import com.google.android.material.bottomnavigation.BottomNavigationView
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : AppCompatActivity(R.layout.activity_main) {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val navHost = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        val navController = navHost.navController

        val bottomNav = findViewById<BottomNavigationView>(R.id.bottomNavigationView)

        bottomNav.setOnItemSelectedListener { item ->
            val navOptions = NavOptions.Builder()
                .setLaunchSingleTop(true)
                .setPopUpTo(navController.graph.startDestinationId, false) // 상태 저장 X
                .build()

            val currentDestId = navController.currentDestination?.id
            val targetDestId = item.itemId

            if (currentDestId == R.id.nav_library && targetDestId != R.id.nav_library) {
                val libraryFragment = navHost.childFragmentManager.fragments
                    .firstOrNull { it is LibraryFragment && it.isVisible } as? LibraryFragment

                if (libraryFragment != null) {
                    libraryFragment.handleLeaveFromLibrary(
                        onLeave = {
                            navController.navigate(targetDestId, null, navOptions)
                        },
                        onCancelled = {}
                    )

                    return@setOnItemSelectedListener false
                }
            }

            return@setOnItemSelectedListener try {
                navController.navigate(item.itemId, null, navOptions)
                true
            } catch (e: IllegalArgumentException) {
                false
            }
        }

        navController.addOnDestinationChangedListener { _, destination, _ ->
            val menu = bottomNav.menu
            for (i in 0 until menu.size()) {
                val menuItem = menu.getItem(i)
                if (destination.id == menuItem.itemId) {
                    menuItem.isChecked = true
                    break
                }
            }
        }
    }
}
