package com.example.librarytogether.network

import android.content.Context

object AuthManager {
    private const val PREF = "auth_prefs"
    private const val KEY_ACCESS = "access_token"
    private const val KEY_REFRESH = "refresh_token"

    fun saveTokens(context: Context, access: String?, refresh: String?) {
        val sp = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
        sp.edit().apply {
            access?.let { putString(KEY_ACCESS, it) }
            refresh?.let { putString(KEY_REFRESH, it) }
        }.apply()
    }

    fun getAccessToken(context: Context): String? =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).getString(KEY_ACCESS, null)

    fun getRefreshToken(context: Context): String? =
        context.getSharedPreferences(PREF, Context.MODE_PRIVATE).getString(KEY_REFRESH, null)

    fun clear(context: Context) {
        val sp = context.getSharedPreferences(PREF, Context.MODE_PRIVATE)
        sp.edit().clear().apply()
    }
}