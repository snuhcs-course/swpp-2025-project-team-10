package com.example.librarytogether.util

import android.content.Context
import android.text.format.DateUtils
import java.time.Instant
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter

object TimeUtils {

    fun parseIsoToMillis(iso: String): Long? = try {
        Instant.parse(iso).toEpochMilli()
    } catch (_: Exception) {
        try {
            OffsetDateTime.parse(iso, DateTimeFormatter.ISO_OFFSET_DATE_TIME)
                .toInstant().toEpochMilli()
        } catch (_: Exception) {
            null
        }
    }

    fun relativeTime(context: Context, iso: String?): CharSequence {
        val created = iso?.let { parseIsoToMillis(it) } ?: return ""
        return DateUtils.getRelativeTimeSpanString(
            created,
            System.currentTimeMillis(),
            DateUtils.MINUTE_IN_MILLIS,
            DateUtils.FORMAT_ABBREV_RELATIVE
        )
    }
}