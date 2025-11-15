package com.example.librarytogether.fake

import com.example.librarytogether.feature.library.data.Book
import com.example.librarytogether.feature.library.data.LibraryRepository
import com.example.librarytogether.feature.library.data.Review
import com.example.librarytogether.feature.library.data.UserProfile
import com.example.librarytogether.library.LibraryFixtures
import javax.inject.Inject

class FakeLibraryRepository @Inject constructor() :
    LibraryRepository(libraryApi = FakeLibraryApi()) {

    private val reviews = mutableListOf<Review>()
    private val books = mutableListOf<Book>()
    private var profile: UserProfile? = LibraryFixtures.profile()

    // 테스트에서 데이터를 제어할 수 있도록 public으로 설정
    var shouldReturnError = false

    fun setReviews(data: List<Review>) {
        reviews.clear()
        reviews.addAll(data)
    }

    fun setBooks(data: List<Book>) {
        books.clear()
        books.addAll(data)
    }

    override suspend fun getMyReviews(): List<Review> {
        return if (shouldReturnError) emptyList() else reviews
    }

    override suspend fun getMyBooks(): List<Book> {
        return if (shouldReturnError) emptyList() else books
    }

    override suspend fun getMyProfile(): UserProfile? {
        return if (shouldReturnError) null else profile
    }

    override suspend fun toggleLike(reviewId: Int): Review? {
        val review = reviews.find { it.id == reviewId }
        review?.let {
            val updatedReview = it.copy(isLiked = !it.isLiked)
            val index = reviews.indexOf(it)
            reviews[index] = updatedReview
            return updatedReview
        }
        return null
    }

}
