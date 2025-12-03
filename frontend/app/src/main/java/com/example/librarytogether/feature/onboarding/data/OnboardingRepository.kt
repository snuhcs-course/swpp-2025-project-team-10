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
        LabelId(1, "채식주의자"),
        LabelId(2, "사피엔스"),
        LabelId(3, "생각의 탄생"),
        LabelId(4, "연금술사"),
        LabelId(5, "백년의 고독"),
        LabelId(6, "82년생 김지영"),
        LabelId(7,"해리포터와 마법사의 돌" ),
        LabelId(8,"살인자의 기억법" ),
        LabelId(9, "미움받을 용기" )
    )

    fun getAuthors() = listOf(
        LabelId(1, "한강"),
        LabelId(2, "무라카미 하루키"),
        LabelId(3, "김영하"),
        LabelId(4, "유발 하라리"),
        LabelId(5, "베르나르 베르베르"),
        LabelId(6, "알랭 드 보통"),
        LabelId(7, "움베르트 에코"),
        LabelId(8,"세이노"),
        LabelId(9, "운동주")
    )

    fun getGenres() = listOf(
        LabelId(1, "현대소설"),
        LabelId(2, "고전소설"),
        LabelId(3, "시"),
        LabelId(4, "자기계발"),
        LabelId(5, "과학·기술"),
        LabelId(6, "인문·사회"),
        LabelId(7, "역사·철학"),
        LabelId(8, "예술·언어"),
        LabelId(9,"경제·경영")
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
