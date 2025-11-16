"""
Django management script to create dummy data for testing.

This script creates:
- Users with profiles, followers, GPS locations
- User tastes and preferences
- Books with various conditions and availability
- Book reviews
- Posts (home feed)
- Comments and likes
- Book collections and wishlists
- Reading statuses
- Barter requests
- Book clubs

Run with: python manage.py shell < create_dummy_data.py
or: python create_dummy_data.py (after setting up Django environment)
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import (
    User, UserTaste, Follow, UserPreferences,
    BookGenre, Author as AuthorChoice, Book as BookChoice,
    BookLength, BookMood, ReadingPurpose
)
from books.models import (
    Genre, Author, Publisher, Book, BookReview,
    BookWishlist, BookCollection, ReadingStatus
)
from social.models import (
    Post, PostLike, Comment, CommentLike, BookClub, BookClubMembership
)
from barter.models import BarterRequest

User = get_user_model()

# ========== Utility Functions ==========

def random_date_in_past(days=365):
    """Generate a random date in the past."""
    return timezone.now() - timedelta(days=random.randint(1, days))

# ========== Data Creation Functions ==========

def create_genres():
    """Create book genres."""
    print("Creating genres...")
    genres_data = [
        ("소설", "Fiction novels and stories"),
        ("에세이", "Personal essays and reflections"),
        ("시", "Poetry collections"),
        ("자기계발", "Self-improvement books"),
        ("과학·기술", "Science and technology"),
        ("인문·사회", "Humanities and social sciences"),
        ("역사·철학", "History and philosophy"),
        ("예술·언어", "Art and language"),
        ("경제·경영", "Economics and business"),
    ]
    
    genres = []
    for name, desc in genres_data:
        genre, created = Genre.objects.get_or_create(
            name=name,
            defaults={"description": desc}
        )
        genres.append(genre)
    
    print(f"  Created/Found {len(genres)} genres")
    return genres

def create_authors():
    """Create authors."""
    print("Creating authors...")
    authors_data = [
        ("한강", "한국의 소설가", "1970-11-27", None, "한국"),
        ("김영하", "한국의 소설가", "1968-11-15", None, "한국"),
        ("정재승", "한국의 뇌과학자", "1972-07-09", None, "한국"),
        ("무라카미 하루키", "일본의 소설가", "1949-01-12", None, "일본"),
        ("F. 스콧 피츠제럴드", "미국의 소설가", "1896-09-24", "1940-12-21", "미국"),
        ("유발 하라리", "이스라엘의 역사학자", "1976-02-24", None, "이스라엘"),
        ("베르나르 베르베르", "프랑스의 소설가", "1961-09-18", None, "프랑스"),
        ("프리드리히 니체", "독일의 철학자", "1844-10-15", "1900-08-25", "독일"),
        ("칼 세이건", "미국의 천문학자", "1934-11-09", "1996-12-20", "미국"),
        ("J.K. 롤링", "영국의 작가", "1965-07-31", None, "영국"),
        ("조지 오웰", "영국의 작가", "1903-06-25", "1950-01-21", "영국"),
        ("헤르만 헤세", "독일의 작가", "1877-07-02", "1962-08-09", "독일"),
        ("알베르 카뮈", "프랑스의 작가", "1913-11-07", "1960-01-04", "프랑스"),
        ("마크 트웨인", "미국의 작가", "1835-11-30", "1910-04-21", "미국"),
        ("톨스토이", "러시아의 작가", "1828-09-09", "1910-11-20", "러시아"),
    ]
    
    authors = []
    for name, bio, birth, death, nationality in authors_data:
        birth_date = datetime.strptime(birth, "%Y-%m-%d").date() if birth else None
        death_date = datetime.strptime(death, "%Y-%m-%d").date() if death else None
        
        author, created = Author.objects.get_or_create(
            name=name,
            defaults={
                "bio": bio,
                "birth_date": birth_date,
                "death_date": death_date,
                "nationality": nationality
            }
        )
        authors.append(author)
    
    print(f"  Created/Found {len(authors)} authors")
    return authors

def create_publishers():
    """Create publishers."""
    print("Creating publishers...")
    publishers_data = [
        ("문학동네", "http://www.munhak.com", 1993, "한국"),
        ("민음사", "http://www.minumsa.com", 1966, "한국"),
        ("창비", "http://www.changbi.com", 1966, "한국"),
        ("김영사", "http://www.gimmyoung.com", 1979, "한국"),
        ("열린책들", "http://www.openbooks.co.kr", 1985, "한국"),
        ("Penguin Books", "http://www.penguin.com", 1935, "영국"),
        ("Random House", "http://www.randomhouse.com", 1927, "미국"),
    ]
    
    publishers = []
    for name, website, year, country in publishers_data:
        publisher, created = Publisher.objects.get_or_create(
            name=name,
            defaults={
                "website": website,
                "founded_year": year,
                "country": country
            }
        )
        publishers.append(publisher)
    
    print(f"  Created/Found {len(publishers)} publishers")
    return publishers

def create_users(count=20):
    """Create dummy users with profiles."""
    print(f"Creating {count} users...")
    
    first_names = ["민준", "서연", "지훈", "하은", "준서", "서현", "도윤", "지우", "시우", "수아",
                   "John", "Emma", "Michael", "Sophia", "David", "Olivia", "James", "Ava", "Robert", "Isabella"]
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임",
                  "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    locations = ["서울", "부산", "대구", "인천", "광주", "대전", "울산", "수원", "성남", "용인"]
    
    bios = [
        "책을 사랑하는 독서가입니다 📚",
        "좋은 책을 나누고 싶어요!",
        "매일 한 권씩 읽기 도전 중",
        "북카페에서 책 읽는 걸 좋아합니다 ☕",
        "다양한 장르를 섭렵하는 중입니다",
        "소설 애호가입니다",
        "인문학 책을 좋아해요",
        "책으로 소통해요 💬",
        "읽은 책은 나눔이 미덕!",
        "Book lover and avid reader 📖",
        "Trading books, sharing stories",
        "Always looking for good reads",
        "Philosophy and fiction enthusiast",
        "Let's exchange books!",
    ]
    
    users = []
    for i in range(count):
        username = f"user{i+1}"
        email = f"user{i+1}@example.com"
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        # Skip if user exists
        if User.objects.filter(username=username).exists():
            users.append(User.objects.get(username=username))
            continue
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password="testpass123",
            first_name=first_name,
            last_name=last_name,
            bio=random.choice(bios),
            location=random.choice(locations),
            birth_date=random_date_in_past(365*40).date(),
            is_profile_public=True,
            allow_direct_messages=True,
            reputation_score=random.randint(0, 500),
            successful_trades=random.randint(0, 50),
            has_initial_taste=random.choice([True, False]),
        )
        users.append(user)
    
    print(f"  Created {len(users)} users")
    return users

def create_user_tastes(users):
    """Create user taste profiles."""
    print("Creating user taste profiles...")
    
    count = 0
    for user in users:
        if user.has_initial_taste and not hasattr(user, 'taste'):
            # Random taste selections
            favorite_genres = random.sample(
                [g.value for g in BookGenre],
                k=random.randint(2, 4)
            )
            favorite_authors = random.sample(
                [a.value for a in AuthorChoice],
                k=random.randint(2, 4)
            )
            favorite_books = random.sample(
                [b.value for b in BookChoice],
                k=random.randint(2, 3)
            )
            preferred_moods = random.sample(
                [m.value for m in BookMood],
                k=random.randint(2, 4)
            )
            reading_purposes = random.sample(
                [r.value for r in ReadingPurpose],
                k=random.randint(2, 3)
            )
            
            UserTaste.objects.create(
                user=user,
                favorite_genres=favorite_genres,
                favorite_authors=favorite_authors,
                favorite_books=favorite_books,
                preferred_length=random.choice([l.value for l in BookLength]),
                preferred_moods=preferred_moods,
                reading_purposes=reading_purposes,
                trade_place_name=random.choice(["스타벅스 강남점", "교보문고", "서울대 도서관", "코엑스 별마당", "홍대 북카페"]),
                trade_address=random.choice(["강남구 테헤란로", "종로구 청계천로", "관악구 서울대입구역", "강남구 삼성동", "마포구 홍대입구역"]),
                current_step=7,
            )
            count += 1
    
    print(f"  Created {count} user taste profiles")

def create_user_preferences(users):
    """Create user preferences."""
    print("Creating user preferences...")
    
    count = 0
    for user in users:
        if not hasattr(user, 'preferences'):
            UserPreferences.objects.create(
                user=user,
                email_notifications=random.choice([True, False]),
                push_notifications=random.choice([True, False]),
                barter_request_notifications=True,
                message_notifications=True,
                follow_notifications=random.choice([True, False]),
                show_email=random.choice([True, False]),
                show_phone=False,
                show_location=True,
                max_barter_distance=random.choice([10, 20, 50, 100]),
            )
            count += 1
    
    print(f"  Created {count} user preferences")

def create_follows(users):
    """Create follow relationships."""
    print("Creating follow relationships...")
    
    follows = []
    for user in users:
        # Each user follows 3-8 random users
        num_to_follow = random.randint(3, 8)
        potential_follows = [u for u in users if u != user]
        to_follow = random.sample(potential_follows, min(num_to_follow, len(potential_follows)))
        
        for followed_user in to_follow:
            follow, created = Follow.objects.get_or_create(
                follower=user,
                following=followed_user
            )
            if created:
                follows.append(follow)
    
    print(f"  Created {len(follows)} follow relationships")
    return follows

def create_books(users, genres, authors, publishers, count=50):
    """Create books owned by users."""
    print(f"Creating {count} books...")
    
    book_titles = [
        "데미안", "사피엔스", "1984", "채식주의자", "코스모스",
        "부의 추월차선", "숨결이 바람 될 때", "불편한 편의점", "어떻게 살 것인가",
        "해리포터와 마법사의 돌", "위대한 개츠비", "이방인", "노인과 바다",
        "호밀밭의 파수꾼", "동물농장", "멋진 신세계", "시간의 역사",
        "총균쇠", "정의란 무엇인가", "생각의 탄생", "지적 대화를 위한 넓고 얕은 지식",
        "미움받을 용기", "아몬드", "82년생 김지영", "완득이", "살인자의 기억법",
        "우리들의 일그러진 영웅", "장미의 이름", "참을 수 없는 존재의 가벼움",
        "백년의 고독", "죄와 벌", "카라마조프가의 형제들", "전쟁과 평화",
        "변신", "그리스인 조르바", "수레바퀴 아래서", "데미안", "나르치스와 골드문트",
        "모모", "끝없는 이야기", "소피의 세계", "연금술사", "오만과 편견",
        "제인 에어", "폭풍의 언덕", "위대한 유산", "오페라의 유령", "레미제라블",
    ]
    
    descriptions = [
        "인생을 바꾸는 명작입니다.",
        "한번 읽으면 멈출 수 없어요!",
        "깊은 감동을 주는 책입니다.",
        "인문학적 통찰이 담긴 책",
        "누구나 읽어야 할 필독서",
        "재미와 의미를 모두 갖춘 책",
        "삶의 지혜를 얻을 수 있습니다",
        "현대인의 필독서",
        "시대를 초월하는 고전",
        "Best seller of the year",
    ]
    
    conditions = ["new", "like_new", "very_good", "good", "acceptable"]
    trade_statuses = ["available", "available", "available", "available", "available", "available", "available", "available" 
                      "pending", "not_available"]
    
    books = []
    for i in range(count):
        owner = random.choice(users)
        title = random.choice(book_titles) + f" (vol.{i+1})"
        
        book = Book.objects.create(
            title=title,
            subtitle=f"부제: {i+1}권" if random.choice([True, False]) else "",
            publisher=random.choice(publishers),
            publication_date=random_date_in_past(3650).date(),
            pages=random.randint(150, 600),
            language=random.choice(["Korean", "English"]),
            description=random.choice(descriptions),
            owner=owner,
            condition=random.choice(conditions),
            trade_status=random.choice(trade_statuses),
            owner_notes=random.choice(["깨끗한 상태입니다", "밑줄 조금 있어요", "상태 좋아요", ""]),
            is_for_barter=random.choice([True, True, True, True, True, False]),  # 83% True
            average_rating=Decimal(str(round(random.uniform(3.0, 5.0), 2))),
            review_count=random.randint(0, 50),
        )
        
        # Add authors
        book.authors.set(random.sample(authors, k=random.randint(1, 2)))
        
        # Add genres
        book.genres.set(random.sample(genres, k=random.randint(1, 3)))
        
        # Add preferred genres for trade
        if book.is_for_barter:
            book.preferred_genres_for_trade.set(random.sample(genres, k=random.randint(1, 2)))
        
        books.append(book)
    
    print(f"  Created {len(books)} books")
    return books

def create_book_reviews(users, books, count=30):
    """Create book reviews."""
    print(f"Creating {count} book reviews...")
    
    review_titles = [
        "정말 좋았어요!",
        "추천합니다",
        "인생책이에요",
        "기대 이상이었습니다",
        "다시 읽고 싶은 책",
        "감동적이었습니다",
        "몰입해서 읽었어요",
        "생각할 거리를 주는 책",
        "Must read!",
        "Highly recommended",
    ]
    
    review_contents = [
        "이 책은 제 인생을 바꿔놓았습니다. 모든 페이지가 의미있고 깊이가 있어요.",
        "처음부터 끝까지 몰입해서 읽었습니다. 정말 추천해요!",
        "작가의 통찰력이 대단해요. 여러번 읽어도 새로운 의미를 발견합니다.",
        "감동적인 스토리와 깊은 메시지가 담겨있어요.",
        "현대를 살아가는 우리에게 꼭 필요한 책입니다.",
        "읽는 내내 생각할 거리가 많았어요. 좋은 책입니다.",
        "기대 이상이었습니다. 주변 사람들에게도 추천하고 있어요.",
        "The author's writing style is captivating. Couldn't put it down!",
        "A masterpiece that everyone should read at least once.",
        "Thought-provoking and beautifully written.",
    ]
    
    reviews = []
    for i in range(count):
        reviewer = random.choice(users)
        book = random.choice(books)
        
        review = BookReview.objects.create(
            book=book,
            reviewer=reviewer,
            book_title=book.title,
            author_name=book.author_names,
            rating=random.randint(3, 5),
            title=random.choice(review_titles),
            content=random.choice(review_contents),
            created_at=random_date_in_past(180),
        )
        
        # Add some helpful votes (likes)
        num_likes = random.randint(0, 10)
        likers = random.sample(users, min(num_likes, len(users)))
        review.helpful_votes.set(likers)
        
        reviews.append(review)
    
    print(f"  Created {len(reviews)} book reviews")
    return reviews

def create_posts(users, books, count=40):
    """Create social posts (home feed)."""
    print(f"Creating {count} posts...")
    
    post_types = ["text", "book_review", "book_recommendation", "reading_update", "barter_success"]
    
    contents = [
        "오늘 읽은 책이 정말 좋았어요! 추천합니다 📚",
        "이번 주 읽을 책 리스트를 정리했어요. 다 읽을 수 있을까요? 😅",
        "드디어 이 책을 다 읽었어요! 감동적이었습니다 ✨",
        "새로운 책을 구했어요! 읽는 게 기대되네요 🎉",
        "북카페에서 책 읽는 시간이 제일 행복해요 ☕",
        "이 책은 정말 인생책이에요. 모두 읽어보세요!",
        "책을 교환했어요! 좋은 거래였습니다 🤝",
        "오늘의 독서 기록: 100페이지 완독!",
        "Just finished an amazing book! Highly recommend it.",
        "Book club meeting was so fun today! 📖",
        "Found a rare book at the bookstore today!",
        "Reading in the park on this beautiful day 🌳",
    ]
    
    posts = []
    for i in range(count):
        author = random.choice(users)
        post_type = random.choice(post_types)
        
        # Get books owned by the author for related_book
        author_books = [book for book in books if book.owner == author]
        related_book = None
        if author_books and random.choice([True, False]):
            related_book = random.choice(author_books)
        
        post = Post.objects.create(
            author=author,
            post_type=post_type,
            content=random.choice(contents),
            related_book=related_book,
            is_public=True,
            created_at=random_date_in_past(90),
        )
        
        # Add likes
        num_likes = random.randint(0, 15)
        likers = random.sample(users, min(num_likes, len(users)))
        for liker in likers:
            PostLike.objects.create(post=post, user=liker)
        
        posts.append(post)
    
    print(f"  Created {len(posts)} posts")
    return posts

def create_comments(users, posts, count=50):
    """Create comments on posts."""
    print(f"Creating {count} comments...")
    
    comment_contents = [
        "정말 공감돼요!",
        "저도 그 책 읽어봤어요. 좋더라고요!",
        "추천 감사합니다 😊",
        "다음에 꼭 읽어봐야겠어요",
        "좋은 정보 감사합니다!",
        "저도 비슷한 경험이 있어요",
        "멋져요! 👍",
        "Great post!",
        "Thanks for sharing!",
        "I totally agree with you.",
    ]
    
    comments = []
    for i in range(count):
        author = random.choice(users)
        post = random.choice(posts)
        
        comment = Comment.objects.create(
            post=post,
            author=author,
            content=random.choice(comment_contents),
            created_at=random_date_in_past(60),
        )
        
        # Add some likes to comments
        num_likes = random.randint(0, 5)
        likers = random.sample(users, min(num_likes, len(users)))
        for liker in likers:
            CommentLike.objects.create(comment=comment, user=liker)
        
        comments.append(comment)
    
    print(f"  Created {len(comments)} comments")
    return comments

def create_wishlists(users, books):
    """Create book wishlists."""
    print("Creating wishlists...")
    
    wishlist_notes = [
        "꼭 읽고 싶어요!",
        "다음에 구매할 책",
        "추천받은 책",
        "읽어야 할 책 리스트",
        "Must read!",
        "",
    ]
    
    wishlists = []
    for user in users:
        # Each user has 3-7 books in wishlist
        num_books = random.randint(3, 7)
        wishlist_books = random.sample(books, min(num_books, len(books)))
        
        for book in wishlist_books:
            wishlist, created = BookWishlist.objects.get_or_create(
                user=user,
                book=book,
                defaults={
                    "priority": random.randint(1, 5),
                    "notes": random.choice(wishlist_notes),
                }
            )
            if created:
                wishlists.append(wishlist)
    
    print(f"  Created {len(wishlists)} wishlist items")
    return wishlists

def create_collections(users, books):
    """Create book collections."""
    print("Creating book collections...")
    
    collection_names = [
        "내 인생 책들",
        "SF 소설 모음",
        "철학 서적",
        "읽은 책",
        "추천 도서",
        "올해의 책",
        "My Favorites",
        "Classic Novels",
        "Must Read Books",
    ]
    
    collections = []
    for user in random.sample(users, k=min(10, len(users))):
        # Each selected user has 1-3 collections
        num_collections = random.randint(1, 3)
        
        # Shuffle collection names for this user to ensure uniqueness
        available_names = collection_names.copy()
        random.shuffle(available_names)
        
        for i in range(num_collections):
            # Use index to ensure unique names per user
            collection_name = available_names[i] if i < len(available_names) else f"컬렉션 {i+1}"
            
            collection, created = BookCollection.objects.get_or_create(
                name=collection_name,
                owner=user,
                defaults={
                    "description": f"{user.username}님의 특별한 책 모음",
                    "is_public": random.choice([True, True, False]),
                }
            )
            
            if created:
                # Add books to collection
                num_books = random.randint(3, 8)
                collection_books = random.sample(books, min(num_books, len(books)))
                collection.books.set(collection_books)
                
                collections.append(collection)
    
    print(f"  Created {len(collections)} book collections")
    return collections

def create_reading_statuses(users, books):
    """Create reading statuses."""
    print("Creating reading statuses...")
    
    statuses = ["want_to_read", "currently_reading", "read", "did_not_finish"]
    notes = [
        "정말 재미있어요!",
        "천천히 읽는 중",
        "완독 목표!",
        "좋은 책이네요",
        "",
    ]
    
    reading_statuses = []
    for user in users:
        # Each user has 5-12 books with reading status
        num_books = random.randint(5, 12)
        status_books = random.sample(books, min(num_books, len(books)))
        
        for book in status_books:
            status = random.choice(statuses)
            
            reading_status = ReadingStatus.objects.create(
                user=user,
                book=book,
                status=status,
                pages_read=random.randint(0, book.pages) if book.pages else 0,
                start_date=random_date_in_past(180).date() if status != "want_to_read" else None,
                finish_date=random_date_in_past(90).date() if status == "read" else None,
                personal_rating=random.randint(3, 5) if status == "read" else None,
                notes=random.choice(notes),
            )
            
            reading_statuses.append(reading_status)
    
    print(f"  Created {len(reading_statuses)} reading statuses")
    return reading_statuses

def create_barter_requests(users, books):
    """Create barter requests with new simplified flow: backend auto-selects books."""
    print("Creating barter requests...")
    
    message_templates = [
        "I'd like to offer '{}' for exchange.",
        "Would you be interested in '{}'?",
        "This is '{}' from my collection.",
        "이 책 정말 좋아요! 제 컬렉션에 추가하고 싶습니다.",
        "깔끔한 상태의 책입니다. 마음에 드셨으면 좋겠어요.",
        "흥미로운 책이에요. 교환 고려해주세요!",
    ]
    
    # Status choices: pending, completed, rejected
    statuses = ["pending", "pending", "pending", "completed", "rejected"]
    
    barter_requests = []
    for _ in range(15):
        requester = random.choice(users)
        recipient = random.choice([u for u in users if u != requester])
        
        # Get books from each user
        requester_books = list(requester.books.filter(is_for_barter=True, trade_status="available"))
        recipient_books = list(recipient.books.filter(is_for_barter=True, trade_status="available"))
        
        # Need at least 1 book from each user
        if not recipient_books or not requester_books:
            continue
        
        status = random.choice(statuses)
        requested_book = random.choice(recipient_books)
        
        # Select up to 3 books from requester's available books
        num_offered = min(3, len(requester_books))
        offered_books = random.sample(requester_books, num_offered)
        
        # Generate messages for each offered book
        messages = []
        for book in offered_books:
            template = random.choice(message_templates)
            messages.append(template.format(book.title) if '{}' in template else template)
        
        barter = BarterRequest.objects.create(
            requester=requester,
            recipient=recipient,
            requested_book=requested_book,
            offered_book_ids=[str(book.id) for book in offered_books],
            message="\n---\n".join(messages),
            status=status,
            created_at=random_date_in_past(30),
        )
        
        # Update trade_status based on status
        if status == "pending":
            # Mark all books as not_available
            requested_book.trade_status = "not_available"
            requested_book.save()
            for book in offered_books:
                book.trade_status = "not_available"
                book.save()
        
        elif status == "completed":
            # One of the offered books was accepted
            selected_book = random.choice(offered_books)
            barter.offered_book = selected_book
            barter.completed_date = random_date_in_past(3)
            barter.save()
            
            # Transfer ownership
            requested_book.owner = requester
            requested_book.is_for_barter = False
            requested_book.trade_status = "traded"
            requested_book.save()
            
            selected_book.owner = recipient
            selected_book.is_for_barter = False
            selected_book.trade_status = "traded"
            selected_book.save()
            
            # Restore other non-selected books to available
            for book in offered_books:
                if book.id != selected_book.id:
                    book.trade_status = "available"
                    book.save()
        
        elif status == "rejected":
            # All books restored to available
            barter.response_date = random_date_in_past(7)
            barter.response_message = "죄송하지만 교환이 어려울 것 같습니다."
            barter.save()
            
            requested_book.trade_status = "available"
            requested_book.save()
            for book in offered_books:
                book.trade_status = "available"
                book.save()
        
        barter_requests.append(barter)
    
    print(f"  Created {len(barter_requests)} barter requests")
    return barter_requests


def create_book_clubs(users, books):
    """Create book clubs."""
    print("Creating book clubs...")
    
    club_names = [
        "서울 독서 모임",
        "SF 소설 클럽",
        "인문학 북클럽",
        "영어 원서 읽기",
        "철학 토론 모임",
        "Book Lovers United",
        "Classic Literature Club",
    ]
    
    descriptions = [
        "함께 책을 읽고 이야기를 나누는 모임입니다.",
        "매주 한 권씩 읽고 토론해요!",
        "책을 사랑하는 사람들의 모임",
        "다양한 관점으로 책을 읽어봐요",
        "A community for passionate readers",
        "Let's explore books together!",
    ]
    
    book_clubs = []
    for _ in range(5):
        creator = random.choice(users)
        
        club = BookClub.objects.create(
            name=random.choice(club_names) + f" #{random.randint(1, 100)}",
            description=random.choice(descriptions),
            creator=creator,
            is_public=random.choice([True, True, False]),
            max_members=random.choice([None, 20, 30, 50]),
            current_book=random.choice(books),
        )
        
        # Add moderators
        num_moderators = random.randint(1, 3)
        moderators = random.sample([u for u in users if u != creator], min(num_moderators, len(users)-1))
        club.moderators.set(moderators)
        
        # Add members
        num_members = random.randint(5, 15)
        members = random.sample(users, min(num_members, len(users)))
        for member in members:
            BookClubMembership.objects.create(
                club=club,
                user=member,
                role="member",
                joined_at=random_date_in_past(60),
            )
        
        book_clubs.append(club)
    
    print(f"  Created {len(book_clubs)} book clubs")
    return book_clubs

# ========== Main Execution ==========

def main():
    """Main function to create all dummy data."""
    print("=" * 60)
    print("Creating Dummy Test Data")
    print("=" * 60)
    
    try:
        # Create base data
        genres = create_genres()
        authors = create_authors()
        publishers = create_publishers()
        
        # Create users and relationships
        users = create_users(count=20)
        create_user_tastes(users)
        create_user_preferences(users)
        create_follows(users)
        
        # Create books
        books = create_books(users, genres, authors, publishers, count=50)
        
        # Create reviews and social content
        create_book_reviews(users, books, count=30)
        posts = create_posts(users, books, count=40)
        create_comments(users, posts, count=50)
        
        # Create user book interactions
        create_wishlists(users, books)
        create_collections(users, books)
        create_reading_statuses(users, books)
        
        # Create barter requests
        create_barter_requests(users, books)
        
        # Create book clubs
        create_book_clubs(users, books)
        
        print("=" * 60)
        print("✅ Dummy data creation completed successfully!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  Users: {User.objects.count()}")
        print(f"  Books: {Book.objects.count()}")
        print(f"  Reviews: {BookReview.objects.count()}")
        print(f"  Posts: {Post.objects.count()}")
        print(f"  Comments: {Comment.objects.count()}")
        print(f"  Wishlists: {BookWishlist.objects.count()}")
        print(f"  Collections: {BookCollection.objects.count()}")
        print(f"  Reading Statuses: {ReadingStatus.objects.count()}")
        print(f"  Barter Requests: {BarterRequest.objects.count()}")
        print(f"  Book Clubs: {BookClub.objects.count()}")
        print(f"  Follows: {Follow.objects.count()}")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
