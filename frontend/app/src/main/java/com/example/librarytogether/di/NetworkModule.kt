package com.example.librarytogether.di

import android.content.Context
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalApi
import com.example.librarytogether.feature.barterapproval.data.BarterApprovalDetail
import com.example.librarytogether.feature.bookdetail.data.BookDetailApi
import com.example.librarytogether.feature.explore.data.ExploreApi
import com.example.librarytogether.feature.home.data.HomeApi
import com.example.librarytogether.feature.library.data.LibraryApi
import com.example.librarytogether.feature.notification.data.NotificationApi
import com.example.librarytogether.feature.onboarding.data.OnboardingApi
import com.example.librarytogether.feature.profile.data.ProfileApi
import com.example.librarytogether.feature.search.data.SearchApi
import com.example.librarytogether.network.RetrofitClient
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import retrofit2.Retrofit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideRetrofit(@ApplicationContext context: Context): Retrofit {
        return RetrofitClient.getClient(context)
    }

    @Provides
    @Singleton
    fun provideHomeApi(retrofit: Retrofit): HomeApi {
        return retrofit.create(HomeApi::class.java)
    }

    @Provides
    @Singleton
    fun provideLibraryApi(retrofit: Retrofit): LibraryApi {
        return retrofit.create(LibraryApi::class.java)
    }

    @Provides
    @Singleton
    fun provideSearchApi(retrofit: Retrofit): SearchApi =
        retrofit.create(SearchApi::class.java)

    @Provides
    @Singleton
    fun provideNotificationApi(retrofit: Retrofit): NotificationApi =
        retrofit.create(NotificationApi::class.java)

    @Provides
    @Singleton
    fun provideOnboardingApi(retrofit: Retrofit): OnboardingApi =
        retrofit.create(OnboardingApi::class.java)

    @Provides
    @Singleton
    fun provideProfileApi(retrofit: Retrofit): ProfileApi =
        retrofit.create(ProfileApi::class.java)

    @Provides
    @Singleton
    fun provideExploreApi(retrofit: Retrofit): ExploreApi =
        retrofit.create(ExploreApi::class.java)

    @Provides
    @Singleton
    fun provideBookDetailApi(retrofit: Retrofit): BookDetailApi =
        retrofit.create(BookDetailApi::class.java)

    @Provides
    @Singleton
    fun barterApprovalApi(retrofit: Retrofit): BarterApprovalApi =
        retrofit.create(BarterApprovalApi::class.java)
}
