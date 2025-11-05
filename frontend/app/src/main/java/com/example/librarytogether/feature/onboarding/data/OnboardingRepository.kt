package com.example.librarytogether.feature.onboarding.data

import android.util.Log
import com.example.librarytogether.feature.onboarding.data.*
import javax.inject.Inject

class OnboardingRepository @Inject constructor(
    private val api: OnboardingApi
) {
    private val selectedBooks = mutableListOf<Int>()
    private val selectedAuthors = mutableListOf<Int>()
    private val selectedGenres = mutableListOf<Int>()

    fun getBooks() = listOf(
        LabelId(1, "해리포터"),
        LabelId(2, "데미안"),
        LabelId(3, "나미야 잡화점의 기적"),
        LabelId(4, "달러구트 꿈 백화점"),
        LabelId(5, "1984")
    )

    fun getAuthors() = listOf(
        LabelId(1, "J.K. 롤링"),
        LabelId(2, "무라카미 하루키"),
        LabelId(3, "조앤 조지"),
        LabelId(4, "조지 오웰"),
        LabelId(5, "히가시노 게이고")
    )

    fun getGenres() = listOf(
        LabelId(1, "판타지"),
        LabelId(2, "로맨스"),
        LabelId(3, "추리"),
        LabelId(4, "SF"),
        LabelId(5, "에세이")
    )

    fun saveSelection(step: Int, ids: List<Int>) {
        when (step) {
            0 -> {
                selectedBooks.clear()
                selectedBooks.addAll(ids)
            }
            1 -> {
                selectedAuthors.clear()
                selectedAuthors.addAll(ids)
            }
            2 -> {
                selectedGenres.clear()
                selectedGenres.addAll(ids)
            }
        }
    }


    suspend fun submitSelections(): Boolean {
        val req = OnboardingSubmitRequest(
            book_ids = selectedBooks,
            author_ids = selectedAuthors,
            genre_ids = selectedGenres
        )
        return try {
            api.submit(req).isSuccessful
        } catch (e: Exception) {
            Log.e("OnboardingRepo", "submitSelections", e)
            false
        }
    }
}


// Upgrade 할 버전. But not now
//** class OnboardingRepository @Inject constructor(
//    private val api: OnboardingApi
//) {
//    // State is can be REMOVED from the repository.
//
//    fun getBooks(): List<LabelId> { ... }
//    fun getAuthors(): List<LabelId> { ... }
//    fun getGenres(): List<LabelId> { ... }
//
//    // This function now takes all selections at once.
//    suspend fun submitSelections(
//        bookIds: List<Int>,
//        authorIds: List<Int>,
//        genreIds: List<Int>
//    ): Boolean {
//        val req = OnboardingSubmitRequest(
//            book_ids = bookIds,
//            author_ids = authorIds,
//            genre_ids = genreIds
//        )
//        return try {
//            val response = api.submit(req)
//            Log.d("OnboardingRepo", "Submit successful: ${response.isSuccessful}")
//            response.isSuccessful
//        } catch (e: Exception) {
//            Log.e("OnboardingRepo", "submitSelections failed", e)
//            false
//        }
//    }
//}
