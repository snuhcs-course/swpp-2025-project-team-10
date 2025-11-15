package com.example.librarytogether.feature.onboarding.data

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

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
        LabelId(1, "현대소설"),
        LabelId(2, "고전소설"),
        LabelId(3, "에세이"),
        LabelId(4, "시/희곡"),
        LabelId(5, "과학·기술"),
        LabelId(6, "인문·사회"),
        LabelId(7, "역사·철학"),
        LabelId(8, "예술·언어")
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
