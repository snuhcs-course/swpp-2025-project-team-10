package com.example.librarytogether.di

import com.example.librarytogether.feature.home.data.HomeApi
import com.example.librarytogether.feature.home.data.HomeRepository
import com.example.librarytogether.feature.library.data.LibraryApi
import com.example.librarytogether.feature.library.data.LibraryRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides
    @Singleton
    fun provideLibraryRepository(libraryApi: LibraryApi): LibraryRepository {
        return LibraryRepository(libraryApi)
    }

//     @Provides
//     @Singleton
//     fun provideHomeRepository(homeApi: HomeApi): HomeRepository {
//         return HomeRepository(homeApi)
//     }
}
