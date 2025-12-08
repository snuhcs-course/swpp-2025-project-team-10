package com.example.librarytogether.feature.home

import com.example.librarytogether.feature.home.data.Post

interface PostSorter {
    fun sort(posts: List<Post>, region: String? = null): List<Post>
}

class LatestSorter : PostSorter {
    override fun sort(posts: List<Post>, region: String?): List<Post> {
        return posts.sortedByDescending { it.createdAt }
    }
}

class PopularSorter : PostSorter {
    override fun sort(posts: List<Post>, region: String?): List<Post> {
        return posts.sortedByDescending { it.likeCount }
    }
}

class NearbySorter : PostSorter {
    override fun sort(posts: List<Post>, region: String?): List<Post> {
        val targetRegion = region?.trim()?.takeIf { it.length >= 2 }?.take(2)

        val filtered = if (targetRegion.isNullOrBlank()) {
            posts
        } else {
            posts.filter { post ->
                val posterRegion = post.posterLocation
                    ?.trim()
                    ?.takeIf { it.length >= 2 }
                    ?.take(2)
                posterRegion == targetRegion
            }
        }
        return filtered.sortedByDescending { it.createdAt }
    }
}

object PostSorterFactory {
    fun create(type: SortType): PostSorter {
        return when (type) {
            SortType.LATEST -> LatestSorter()
            SortType.POPULAR -> PopularSorter()
            SortType.NEARBY -> NearbySorter()
        }
    }
}
