package com.example.librarytogether.feature.main

import androidx.lifecycle.Lifecycle
import androidx.navigation.NavController
import androidx.navigation.fragment.NavHostFragment
import androidx.test.core.app.ActivityScenario
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.click
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.runner.AndroidJUnit4
import com.example.librarytogether.R
import com.google.android.material.bottomnavigation.BottomNavigationView
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import dagger.hilt.android.testing.HiltTestApplication
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowAlertDialog
import org.robolectric.shadows.ShadowLooper

@HiltAndroidTest
@Config(application = HiltTestApplication::class, sdk = [33])
@RunWith(AndroidJUnit4::class)
class MainActivityTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testNavigation_HomeToLibrary_andBackToHome() {
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            scenario.moveToState(Lifecycle.State.RESUMED)

            // 1. 초기 상태: Home 확인
            scenario.onActivity { activity ->
                val navController = getNavController(activity)
                assertEquals(R.id.nav_home, navController.currentDestination?.id)
            }

            // 2. Library 탭 클릭 (Home -> Library)
            // -> else 분기 (NavOptions 사용 이동) 실행
            onView(withId(R.id.nav_library)).perform(click())
            ShadowLooper.runUiThreadTasksIncludingDelayedTasks()

            scenario.onActivity { activity ->
                val navController = getNavController(activity)
                assertEquals(R.id.nav_library, navController.currentDestination?.id)
            }

            // 3. Home 탭 클릭 (Library -> Home)
            // -> MainActivity의 handleLeaveFromLibrary 로직 진입
            onView(withId(R.id.nav_home)).perform(click())
            ShadowLooper.runUiThreadTasksIncludingDelayedTasks()

            // [핵심] LibraryFragment가 종료 확인 다이얼로그를 띄웠을 경우 처리
            // (401 에러나 Edit 모드 등으로 인해 다이얼로그가 떴다면 여기서 수락해야 함)
            val dialog = ShadowAlertDialog.getLatestAlertDialog()
            dialog?.let {
                // 다이얼로그가 있다면 Positive Button(확인/나가기) 클릭
                it.getButton(android.content.DialogInterface.BUTTON_POSITIVE).performClick()
                ShadowLooper.runUiThreadTasksIncludingDelayedTasks()
            }

            // 4. 최종 상태: Home 확인 (popBackStack 로직 검증)
            scenario.onActivity { activity ->
                val navController = getNavController(activity)
                assertEquals("Should navigate back to Home", R.id.nav_home, navController.currentDestination?.id)
            }
        }
    }

    @Test
    fun testNavigation_Reselection_DoesNothing() {
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            scenario.moveToState(Lifecycle.State.RESUMED)

            // 1. Home 상태에서 Home 다시 클릭 (Reselection)
            // -> currentDestId == targetDestId 분기 실행
            onView(withId(R.id.nav_home)).perform(click())
            ShadowLooper.runUiThreadTasksIncludingDelayedTasks()

            scenario.onActivity { activity ->
                val navController = getNavController(activity)
                assertEquals(R.id.nav_home, navController.currentDestination?.id)
            }
        }
    }

    @Test
    fun testNavigation_PopStackBehavior() {
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            scenario.moveToState(Lifecycle.State.RESUMED)

            // 1. Library로 이동
            onView(withId(R.id.nav_library)).perform(click())
            ShadowLooper.runUiThreadTasksIncludingDelayedTasks()

            // 2. 다시 Home으로 이동
            onView(withId(R.id.nav_home)).perform(click())
            ShadowLooper.runUiThreadTasksIncludingDelayedTasks()

            // 혹시 모를 다이얼로그 처리
            ShadowAlertDialog.getLatestAlertDialog()?.getButton(android.content.DialogInterface.BUTTON_POSITIVE)?.performClick()
            ShadowLooper.runUiThreadTasksIncludingDelayedTasks()

            scenario.onActivity { activity ->
                val navController = getNavController(activity)
                assertEquals(R.id.nav_home, navController.currentDestination?.id)
            }
        }
    }

    @Test
    fun testDestinationChangedListener_UpdatesBottomNavSelection() {
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            scenario.moveToState(Lifecycle.State.RESUMED)

            // 1. NavController를 통해 코드로 네비게이션 수행 (Click 이벤트 아님)
            // -> addOnDestinationChangedListener 로직 검증
            scenario.onActivity { activity ->
                val navController = getNavController(activity)
                navController.navigate(R.id.nav_library)
            }
            ShadowLooper.runUiThreadTasksIncludingDelayedTasks()

            // 2. BottomNavigationView의 선택 상태 확인
            // [수정] ClassCastException 해결: withId(R.id.bottomNavigationView) 사용
            onView(withId(R.id.bottomNavigationView)).check { view, _ ->
                val bottomNav = view as BottomNavigationView
                assertEquals(R.id.nav_library, bottomNav.selectedItemId)
            }
        }
    }

    private fun getNavController(activity: MainActivity): NavController {
        val navHostFragment = activity.supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        return navHostFragment.navController
    }
}
