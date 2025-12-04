package com.example.librarytogether.feature.onboarding.data

import android.util.Log
import javax.inject.Inject
import javax.inject.Singleton

class OnboardingRepository @Inject constructor(
    private val api: OnboardingApi
) {

    private val selectedBooks = mutableListOf<String>()
    private val selectedAuthors = mutableListOf<String>()
    private val selectedGenres = mutableListOf<String>()

    fun getBooks() = listOf(
        LabelId(1, "채식주의자"),
        LabelId(2, "사피엔스"),
        LabelId(3, "데미안"),
        LabelId(4, "코스모스"),
        LabelId(5, "총균쇠"),
        LabelId(6, "82년생 김지영"),
        LabelId(7,"우리들의 일그러진 영웅" ),
        LabelId(8,"살인자의 기억법" ),
        LabelId(9, "미움받을 용기" )
    )

    fun getAuthors() = listOf(
        LabelId(1, "한강"),
        LabelId(2, "무라카미 하루키"),
        LabelId(3, "김영하"),
        LabelId(4, "유발 하라리"),
        LabelId(5, "베르나르 베르베르"),
        LabelId(6, "마이클 샌델"),
        LabelId(7, "톨스토이"),
        LabelId(8,"정재승"),
        LabelId(9, "유시민")
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

    fun saveSelection(step: Int, ids: List<String>) {
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
            // 백엔드 Serializer가 String과 Int를 모두 처리하므로, 그대로 전송
            book_ids = selectedBooks,
            author_ids = selectedAuthors.mapNotNull { it.toIntOrNull() },
            genre_ids = selectedGenres.mapNotNull { it.toIntOrNull() }
        )
        Log.d("OnboardingRepository", "Submitting: $req")
        val response = api.submit(req)
        return response.isSuccessful
    }
}
