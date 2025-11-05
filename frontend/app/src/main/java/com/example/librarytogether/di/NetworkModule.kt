package com.example.librarytogether.di

import android.content.Context
import com.example.librarytogether.feature.barter.data.BarterApi
import com.example.librarytogether.feature.home.data.HomeApi
import com.example.librarytogether.feature.library.data.LibraryApi
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
    fun provideBarterApi(retrofit: Retrofit): BarterApi {
        return retrofit.create(BarterApi::class.java)
    }

    @Provides
    @Singleton
    fun provideSearchApi(retrofit: Retrofit): SearchApi =
        retrofit.create(SearchApi::class.java)

}
