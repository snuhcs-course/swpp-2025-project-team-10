package com.example.librarytogether.fake

import com.example.librarytogether.feature.library.data.*
import retrofit2.Response

class FakeLibraryApi : LibraryApi {
    override suspend fun getMyReviews(): Response<ReviewResponse> {
        return Response.success(ReviewResponse(results = emptyList()))
    }

    override suspend fun addReview(review: PostReview): Response<Unit> {
        return Response.success(Unit)
    }

    override suspend fun toggleReviewLike(reviewId: Int): Response<Review> {
        return Response.success(null)
    }

    override suspend fun getMyBooks(): Response<List<Book>> {
        return Response.success(emptyList())
    }

    override suspend fun getMyProfile(): Response<UserProfile> {
        return Response.success(null)
    }

    override suspend fun updateMyProfile(profile: UserProfile): Response<UserProfile> {
        return Response.success(null)
    }

    override suspend fun getMyWishlist(): Response<List<Book>> {
        return Response.success(emptyList())
    }
}

