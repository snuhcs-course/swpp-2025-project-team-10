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
    Genre, Author, Publisher, Translator, 
    BookPublication, BookCopy, BookReview,
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
        ("현대소설", "MODERN_FICTION"),
        ("고전소설", "CLASSIC_FICTION"),
        ("시", "POETRY_DRAMA"),
        ("자기계발", "SELF_HELP"),
        ("과학·기술", "SCIENCE_TECH"),
        ("인문·사회", "HUMANITIES_SOCIAL"),
        ("역사·철학", "HISTORY_PHILOSOPHY"),
        ("예술·언어", "ART_LANGUAGE"),
        ("경제·경영", "ECONOMICS_BUSINESS"),
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
        ("엠제이 드마코", "미국의 작가", None, None, "미국"),
        ("폴 칼라니티", "미국의 의사/작가", None, None, "미국"),
        ("김호연", "한국의 소설가", None, None, "한국"),
        ("유시민", "한국의 작가", None, None, "한국"),
        ("어니스트 헤밍웨이", "미국의 소설가", "1899-07-21", "1961-07-02", "미국"),
        ("J.D. 샐린저", "미국의 소설가", "1919-01-01", "2010-01-27", "미국"),
        ("올더스 헉슬리", "영국의 소설가", "1894-07-26", "1963-11-22", "영국"),
        ("스티븐 호킹", "영국의 물리학자", "1942-01-08", "2018-03-14", "영국"),
        ("재레드 다이아몬드", "미국의 생리학자", None, None, "미국"),
        ("마이클 샌델", "미국의 정치철학자", None, None, "미국"),
        ("로버트 루트번스타인", "미국의 생화학자", None, None, "미국"),
        ("채사장", "한국의 작가", None, None, "한국"),
        ("기시미 이치로", "일본의 철학자", None, None, "일본"),
        ("손원평", "한국의 소설가", None, None, "한국"),
        ("조남주", "한국의 소설가", None, None, "한국"),
        ("김려령", "한국의 소설가", None, None, "한국"),
        ("이문열", "한국의 소설가", None, None, "한국"),
        ("움베르토 에코", "이탈리아의 작가", "1932-01-05", "2016-02-19", "이탈리아"),
        ("밀란 쿤데라", "체코의 소설가", "1929-04-01", "2023-07-11", "체코"),
        ("가브리엘 가르시아 마르케스", "콜롬비아의 소설가", "1927-03-06", "2014-04-17", "콜롬비아"),
        ("도스토예프스키", "러시아의 소설가", "1821-11-11", "1881-02-09", "러시아"),
        ("프란츠 카프카", "오스트리아의 소설가", "1883-07-03", "1924-06-03", "오스트리아"),
        ("니코스 카잔차키스", "그리스의 소설가", "1883-02-18", "1957-10-26", "그리스"),
        ("미하엘 엔데", "독일의 작가", "1929-11-12", "1995-08-28", "독일"),
        ("요스테인 가더", "노르웨이의 작가", "1952-08-08", None, "노르웨이"),
        ("파울로 코엘료", "브라질의 작가", "1947-08-24", None, "브라질"),
        ("제인 오스틴", "영국의 소설가", "1775-12-16", "1817-07-18", "영국"),
        ("샬럿 브론테", "영국의 소설가", "1816-04-21", "1855-03-31", "영국"),
        ("에밀리 브론테", "영국의 소설가", "1818-07-30", "1848-12-19", "영국"),
        ("찰스 디킨스", "영국의 소설가", "1812-02-07", "1870-06-09", "영국"),
        ("가스통 르루", "프랑스의 소설가", "1868-05-06", "1927-04-15", "프랑스"),
        ("빅토르 위고", "프랑스의 소설가", "1802-02-26", "1885-05-22", "프랑스"),
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
            has_initial_taste=False,
        )
        users.append(user)
    
    print(f"  Created {len(users)} users")
    return users

def create_user_tastes(users):
    """Create user taste profiles."""
    print("Creating user taste profiles...")
    
    count = 0
    # 한글 매핑 테이블
    genre_ko = {
        "MODERN_FICTION": "현대소설",
        "CLASSIC_FICTION": "고전소설",
        "ESSAY": "에세이",
        "POETRY_DRAMA": "시/희곡",
        "SELF_HELP": "자기계발",
        "SCIENCE_TECH": "과학·기술",
        "HUMANITIES_SOCIAL": "인문·사회",
        "HISTORY_PHILOSOPHY": "역사·철학",
        "ART_LANGUAGE": "예술·언어",
    }
    author_ko = {a.value: a.label if hasattr(a, 'label') else a.value for a in AuthorChoice}
    book_ko = {b.value: b.label if hasattr(b, 'label') else b.value for b in BookChoice}

    # 지역별 거래장소 및 주소 데이터
    region_places = [
        {"address": "서울특별시 강남구", "places": ["교보문고 강남점", "스타벅스 강남역점", "강남구청 도서관"]},
        {"address": "서울특별시 관악구", "places": ["서울대 도서관", "관악구 북카페", "관악구청 도서관"]},
        {"address": "서울특별시 마포구", "places": ["홍대 북카페", "마포구청 도서관", "홍대입구역 북라운지"]},
        {"address": "부산광역시 해운대구", "places": ["해운대 도서관", "해운대 북카페", "해운대구청 도서관"]},
        {"address": "대구광역시 수성구", "places": ["수성구 도서관", "수성구 북카페", "수성구청 도서관"]},
        {"address": "경기도 성남시", "places": ["성남시 도서관", "성남 북카페", "성남시청 도서관"]},
        {"address": "경기도 용인시", "places": ["용인시 도서관", "용인 북카페", "용인시청 도서관"]},
        {"address": "충청남도 서천군", "places": ["서천군 도서관", "서천 북카페", "서천군청 도서관"]},
        {"address": "강원도 춘천시", "places": ["춘천시 도서관", "춘천 북카페", "춘천시청 도서관"]},
        {"address": "전라북도 전주시", "places": ["전주시 도서관", "전주 북카페", "전주시청 도서관"]},
        {"address": "경상북도 포항시", "places": ["포항시 도서관", "포항 북카페", "포항시청 도서관"]},
        {"address": "제주특별자치도 제주시", "places": ["제주시 도서관", "제주 북카페", "제주시청 도서관"]},
        # 필요시 더 추가
    ]

    for user in users:
        if not user.has_initial_taste and not hasattr(user, 'taste'):
            # Random taste selections
            favorite_genres_en = random.sample([g.value for g in BookGenre], k=random.randint(2, 4))
            favorite_genres = [genre_ko.get(g, g) for g in favorite_genres_en]
            favorite_authors_en = random.sample([a.value for a in AuthorChoice], k=random.randint(2, 4))
            favorite_authors = [author_ko.get(a, a) for a in favorite_authors_en]
            favorite_books_en = random.sample([b.value for b in BookChoice], k=random.randint(2, 3))
            favorite_books = [book_ko.get(b, b) for b in favorite_books_en]
            preferred_moods = random.sample([m.value for m in BookMood], k=random.randint(2, 4))
            reading_purposes = random.sample([r.value for r in ReadingPurpose], k=random.randint(2, 3))

            # 지역 랜덤 선택
            region = random.choice(region_places)
            trade_address = region["address"]
            trade_place_name = random.choice(region["places"])

            UserTaste.objects.create(
                user=user,
                favorite_genres=favorite_genres,
                favorite_authors=favorite_authors,
                favorite_books=favorite_books,
                preferred_length=random.choice([l.value for l in BookLength]),
                preferred_moods=preferred_moods,
                reading_purposes=reading_purposes,
                trade_place_name=trade_address,
                trade_address=trade_place_name,
                current_step=7,
            )
            count += 1
    
    print(f"  Created {count} user taste profiles")

def create_user_preferences(users):
    """Create user preferences with book/author notes and reading habits."""
    print("Creating user preferences...")
    
    import json
    
    book_notes = [
        "이 책이 제 인생을 바꿔놓았습니다",
        "여러 번 읽어도 새로운 감동",
        "추천하고 싶은 책",
        "깊은 여운이 남는 작품",
        "잊을 수 없는 명작",
        "읽는 내내 몰입하게 됩니다",
        "생각할 거리를 많이 주는 책",
        "친구에게 꼭 추천하고 싶어요",
        "마음이 따뜻해지는 이야기",
        "현실을 돌아보게 하는 책",
        "읽고 나서 오랫동안 기억에 남아요",
        "삶에 대한 새로운 시각을 얻었습니다",
        "가볍게 읽기 좋은 책",
        "휴식 시간에 딱 맞는 책",
        "감동과 재미를 모두 잡은 작품",
    ]

    author_notes = [
        "이 작가의 모든 작품을 읽었어요",
        "독특한 문체가 매력적",
        "깊이 있는 통찰력",
        "감성적인 표현이 좋아요",
        "철학적 사고를 자극해요",
        "다양한 장르를 넘나드는 작가",
        "작품마다 새로운 시도를 하는 작가",
        "인물 묘사가 뛰어나요",
        "스토리텔링이 탁월합니다",
        "현실과 상상을 잘 버무리는 작가",
        "읽을 때마다 새로운 느낌을 줍니다",
        "문장 하나하나가 인상적입니다",
        "작가의 세계관이 독특해요",
        "작품마다 깊은 메시지가 담겨 있습니다",
    ]

    reading_habits = [
        "주로 저녁에 읽어요",
        "카페에서 읽는 걸 좋아해요",
        "매일 한 시간씩 읽기",
        "주말에 몰아서 읽기",
        "출퇴근 시간에 읽어요",
        "자기 전 독서",
        "아침에 일어나서 한 챕터씩",
        "점심시간에 잠깐씩",
        "여행 갈 때 꼭 책을 챙겨요",
        "비 오는 날엔 집에서 독서",
        "도서관에서 집중해서 읽기",
        "산책하면서 오디오북 듣기",
        "가끔은 밤새워 읽기도 해요",
    ]
    
    count = 0
    for user in users:
        if not hasattr(user, 'preferences'):
            # Create preference metadata
            metadata = {}
            
            # Add random notes if user has initial taste
            if not user.has_initial_taste:
                # Add book notes (1-3 notes)
                num_book_notes = random.randint(1, 3)
                metadata["favBookNotes"] = random.sample(book_notes, num_book_notes)
                
                # Add author notes (1-3 notes)
                num_author_notes = random.randint(1, 3)
                metadata["favAuthorNotes"] = random.sample(author_notes, num_author_notes)
                
                # Add reading habit
                metadata["readingHabit"] = random.choice(reading_habits)
            
            # Create UserPreferences with metadata
            prefs = UserPreferences.objects.create(
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
                preferred_meeting_locations=json.dumps(metadata) if metadata else "",
            )
            count += 1
            user.has_initial_taste = True
            user.save()
    
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
    """Create book publications and copies owned by users."""
    print(f"Creating {count} book publications and copies...")
    
    books_data = [
        {"title": "데미안", "author": "헤르만 헤세"},
        {"title": "사피엔스", "author": "유발 하라리"},
        {"title": "1984", "author": "조지 오웰"},
        {"title": "채식주의자", "author": "한강"},
        {"title": "코스모스", "author": "칼 세이건"},
        {"title": "부의 추월차선", "author": "엠제이 드마코"},
        {"title": "숨결이 바람 될 때", "author": "폴 칼라니티"},
        {"title": "불편한 편의점", "author": "김호연"},
        {"title": "어떻게 살 것인가", "author": "유시민"},
        {"title": "해리포터와 마법사의 돌", "author": "J.K. 롤링"},
        {"title": "위대한 개츠비", "author": "F. 스콧 피츠제럴드"},
        {"title": "이방인", "author": "알베르 카뮈"},
        {"title": "노인과 바다", "author": "어니스트 헤밍웨이"},
        {"title": "호밀밭의 파수꾼", "author": "J.D. 샐린저"},
        {"title": "동물농장", "author": "조지 오웰"},
        {"title": "멋진 신세계", "author": "올더스 헉슬리"},
        {"title": "시간의 역사", "author": "스티븐 호킹"},
        {"title": "총균쇠", "author": "재레드 다이아몬드"},
        {"title": "정의란 무엇인가", "author": "마이클 샌델"},
        {"title": "생각의 탄생", "author": "로버트 루트번스타인"},
        {"title": "지적 대화를 위한 넓고 얕은 지식", "author": "채사장"},
        {"title": "미움받을 용기", "author": "기시미 이치로"},
        {"title": "아몬드", "author": "손원평"},
        {"title": "82년생 김지영", "author": "조남주"},
        {"title": "완득이", "author": "김려령"},
        {"title": "살인자의 기억법", "author": "김영하"},
        {"title": "우리들의 일그러진 영웅", "author": "이문열"},
        {"title": "장미의 이름", "author": "움베르토 에코"},
        {"title": "참을 수 없는 존재의 가벼움", "author": "밀란 쿤데라"},
        {"title": "백년의 고독", "author": "가브리엘 가르시아 마르케스"},
        {"title": "죄와 벌", "author": "도스토예프스키"},
        {"title": "카라마조프가의 형제들", "author": "도스토예프스키"},
        {"title": "전쟁과 평화", "author": "톨스토이"},
        {"title": "변신", "author": "프란츠 카프카"},
        {"title": "그리스인 조르바", "author": "니코스 카잔차키스"},
        {"title": "수레바퀴 아래서", "author": "헤르만 헤세"},
        {"title": "나르치스와 골드문트", "author": "헤르만 헤세"},
        {"title": "모모", "author": "미하엘 엔데"},
        {"title": "끝없는 이야기", "author": "미하엘 엔데"},
        {"title": "소피의 세계", "author": "요스테인 가더"},
        {"title": "연금술사", "author": "파울로 코엘료"},
        {"title": "오만과 편견", "author": "제인 오스틴"},
        {"title": "제인 에어", "author": "샬럿 브론테"},
        {"title": "폭풍의 언덕", "author": "에밀리 브론테"},
        {"title": "위대한 유산", "author": "찰스 디킨스"},
        {"title": "오페라의 유령", "author": "가스통 르루"},
        {"title": "레미제라블", "author": "빅토르 위고"},
        # 필요시 더 추가
    ]
    
    descriptions_general = [
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
        "읽는 내내 몰입하게 됩니다.",
        "생각할 거리를 많이 주는 책입니다.",
        "친구에게 꼭 추천하고 싶어요.",
        "마음이 따뜻해지는 이야기입니다.",
        "현실을 돌아보게 하는 책입니다.",
        "읽고 나서 오랫동안 기억에 남아요.",
        "삶에 대한 새로운 시각을 얻었습니다.",
        "가볍게 읽기 좋은 책입니다.",
        "휴식 시간에 딱 맞는 책입니다.",
        "감동과 재미를 모두 잡은 작품입니다.",
    ]

    descriptions_by_book = {
        "데미안": "자아와 성장에 대한 깊은 통찰을 담은 헤르만 헤세의 대표작입니다. 싱클레어의 내면적 갈등과 성장이 섬세하게 그려져 있습니다. 읽는 내내 자기 자신을 돌아보게 만드는 책입니다.",
        "사피엔스": "유발 하라리가 인류의 역사를 새롭게 해석한 베스트셀러입니다. 인간의 기원과 문명의 발전을 흥미롭게 풀어냅니다. 복잡한 주제를 쉽게 설명해주어 누구나 읽기 좋습니다.",
        "1984": "조지 오웰의 디스토피아 소설로, 전체주의의 위험을 경고합니다. 감시와 통제의 사회에서 인간의 자유와 존엄성을 고민하게 만듭니다. 읽고 나면 현실을 다시 바라보게 됩니다.",
        "채식주의자": "한강의 독특한 문체와 강렬한 메시지가 돋보이는 작품입니다. 인간의 내면과 사회적 억압을 섬세하게 표현합니다. 읽는 내내 불편함과 아름다움이 공존하는 소설입니다.",
        "코스모스": "칼 세이건이 우주의 신비를 쉽게 풀어낸 과학 명저입니다. 과학적 사실과 철학적 사유가 어우러져 있습니다. 우주에 대한 경이로움을 느끼게 해줍니다.",
        "부의 추월차선": "엠제이 드마코가 경제적 자유를 얻는 방법을 현실적으로 제시합니다. 기존의 부에 대한 관념을 뒤집는 통찰이 가득합니다. 실천적인 조언이 많아 동기부여가 됩니다.",
        "숨결이 바람 될 때": "폴 칼라니티의 삶과 죽음에 대한 진솔한 고백이 담겨 있습니다. 의사이자 환자로서의 경험이 깊은 울림을 줍니다. 인생의 의미를 다시 생각하게 만드는 책입니다.",
        "불편한 편의점": "김호연 작가가 그려낸 따뜻한 인간미와 소소한 일상이 담겨 있습니다. 편의점이라는 공간에서 펼쳐지는 다양한 이야기가 공감됩니다. 읽고 나면 마음이 편안해집니다.",
        "어떻게 살 것인가": "유시민의 인생에 대한 철학적 성찰이 담긴 에세이입니다. 삶의 방향성과 가치에 대해 깊이 고민하게 만듭니다. 현실적인 조언과 따뜻한 위로가 있습니다.",
        "해리포터와 마법사의 돌": "J.K. 롤링의 판타지 세계로의 초대, 해리포터 시리즈의 시작입니다. 마법과 우정, 용기가 어우러진 흥미진진한 이야기입니다. 어린이와 어른 모두에게 사랑받는 작품입니다.",
        "위대한 개츠비": "F. 스콧 피츠제럴드가 그려낸 미국의 꿈과 허상, 그리고 사랑의 비극이 담겨 있습니다. 화려함 뒤에 숨겨진 인간의 외로움이 인상적입니다. 시대를 초월한 고전입니다.",
        "이방인": "알베르 카뮈의 부조리와 인간 존재에 대한 탐구가 돋보입니다. 주인공 뫼르소의 무감각함이 독특하게 다가옵니다. 삶과 죽음, 사회적 규범에 대해 생각하게 합니다.",
        "노인과 바다": "어니스트 헤밍웨이의 인간과 자연, 도전의 서사가 담겨 있습니다. 노인의 끈기와 용기가 감동을 줍니다. 간결한 문체 속에 깊은 의미가 숨어 있습니다.",
        "호밀밭의 파수꾼": "J.D. 샐린저가 청춘의 방황을 섬세하게 그려낸 소설입니다. 홀든의 솔직한 시선과 내면의 혼란이 공감됩니다. 성장통을 겪는 모든 이에게 추천합니다.",
        "동물농장": "조지 오웰의 풍자와 사회 비판이 돋보이는 작품입니다. 동물들의 혁명과 그 이후의 변화가 인간 사회를 반영합니다. 짧지만 강렬한 메시지를 전달합니다.",
        "멋진 신세계": "올더스 헉슬리의 미래 사회에 대한 비판적 시각이 담겨 있습니다. 인간의 자유와 행복, 기술의 발전에 대해 고민하게 만듭니다. 읽고 나면 많은 생각이 남는 책입니다.",
        "시간의 역사": "스티븐 호킹이 우주의 기원과 구조를 쉽게 설명합니다. 복잡한 과학 이론을 친절하게 풀어줍니다. 과학에 관심 있는 독자에게 추천합니다.",
        "총균쇠": "재레드 다이아몬드가 인류 문명의 발전을 총, 균, 쇠라는 관점에서 분석합니다. 방대한 자료와 논리가 인상적입니다. 역사와 과학을 함께 즐길 수 있습니다.",
        "정의란 무엇인가": "마이클 샌델이 정의와 도덕, 사회적 가치에 대해 깊이 있게 탐구합니다. 다양한 사례와 토론이 흥미롭습니다. 생각할 거리를 많이 주는 책입니다.",
        "생각의 탄생": "로버트 루트번스타인이 창의성과 사고의 과정을 다양한 예시로 설명합니다. 창의적 사고를 키우고 싶은 사람에게 추천합니다. 읽고 나면 새로운 시각을 얻게 됩니다.",
        "지적 대화를 위한 넓고 얕은 지식": "채사장이 복잡한 사회, 역사, 철학을 쉽게 풀어줍니다. 다양한 분야를 한 권에 담아내어 입문서로 좋습니다. 지적 호기심을 자극하는 책입니다.",
        "미움받을 용기": "기시미 이치로가 아들러 심리학을 바탕으로 용기와 자기 수용을 이야기합니다. 삶의 태도를 바꾸고 싶은 사람에게 추천합니다. 읽고 나면 마음이 가벼워집니다.",
        "아몬드": "손원평 작가가 감정과 성장, 가족의 의미를 섬세하게 그려냅니다. 주인공의 내면적 변화가 인상적입니다. 따뜻하면서도 슬픈 이야기입니다.",
        "82년생 김지영": "조남주 작가가 한국 사회의 여성 문제를 현실적으로 그려냅니다. 김지영의 삶을 통해 공감과 성찰을 이끌어냅니다. 사회적 메시지가 강한 소설입니다.",
        "완득이": "김려령 작가가 청소년의 성장과 가족, 우정의 이야기를 따뜻하게 풀어냅니다. 유쾌하면서도 감동적인 스토리입니다. 읽고 나면 미소가 지어집니다.",
        "살인자의 기억법": "김영하 작가가 독특한 시점과 심리 묘사로 긴장감을 높입니다. 치매에 걸린 살인자의 내면이 흥미롭게 그려집니다. 마지막까지 눈을 뗄 수 없는 소설입니다.",
        "우리들의 일그러진 영웅": "이문열 작가가 권력과 인간 심리를 학교라는 공간에서 날카롭게 분석합니다. 짧지만 강렬한 메시지가 있습니다. 한국 현대문학의 대표작입니다.",
        "장미의 이름": "움베르토 에코가 중세 수도원을 배경으로 미스터리와 철학을 결합합니다. 복잡한 플롯과 깊은 사유가 인상적입니다. 지적 호기심을 자극하는 소설입니다.",
        "참을 수 없는 존재의 가벼움": "밀란 쿤데라가 사랑과 존재, 자유에 대해 철학적으로 탐구합니다. 인물들의 내면적 갈등이 깊이 있게 그려집니다. 읽고 나면 오랫동안 여운이 남습니다.",
        "백년의 고독": "가브리엘 가르시아 마르케스가 마법적 리얼리즘으로 가족의 역사를 그려냅니다. 환상과 현실이 어우러진 독특한 분위기입니다. 세계문학의 걸작입니다.",
        "죄와 벌": "도스토예프스키가 인간의 죄와 구원, 내면의 갈등을 심도 있게 다룹니다. 라스콜리니코프의 심리 변화가 인상적입니다. 러시아 문학의 정수를 느낄 수 있습니다.",
        "카라마조프가의 형제들": "도스토예프스키가 가족과 신, 인간 본성에 대해 깊이 있게 탐구합니다. 복잡한 인물 관계와 철학적 대화가 돋보입니다. 읽고 나면 많은 생각이 남는 책입니다.",
        "전쟁과 평화": "톨스토이가 러시아의 역사와 인간의 삶을 방대한 스케일로 그려냅니다. 사랑과 전쟁, 평화에 대한 깊은 사유가 담겨 있습니다. 고전문학의 진수를 느낄 수 있습니다.",
        "변신": "프란츠 카프카가 인간 소외와 불안, 존재의 의미를 독특하게 표현합니다. 주인공 그레고르의 변화가 상징적으로 다가옵니다. 읽고 나면 묘한 여운이 남습니다.",
        "그리스인 조르바": "니코스 카잔차키스가 자유와 삶의 열정을 조르바라는 인물을 통해 보여줍니다. 인생을 즐기는 태도와 철학이 인상적입니다. 읽고 나면 삶에 대한 용기가 생깁니다.",
        "수레바퀴 아래서": "헤르만 헤세가 청소년의 성장과 사회적 억압을 섬세하게 그려냅니다. 한스의 내면적 갈등이 공감됩니다. 슬프면서도 아름다운 이야기입니다.",
        "나르치스와 골드문트": "헤르만 헤세가 예술과 삶, 사랑에 대한 철학적 사유를 담았습니다. 두 인물의 대조적 삶이 인상적입니다. 깊은 여운을 남기는 소설입니다.",
        "모모": "미하엘 엔데가 시간의 소중함과 인간관계를 따뜻하게 그려냅니다. 모모의 순수함이 감동을 줍니다. 어린이와 어른 모두에게 추천합니다.",
        "끝없는 이야기": "미하엘 엔데가 상상력과 모험, 성장의 의미를 환상적으로 풀어냅니다. 바스티안의 모험이 흥미진진합니다. 읽고 나면 상상력이 풍부해집니다.",
        "소피의 세계": "요스테인 가더가 철학의 역사를 소피의 시선으로 쉽게 설명합니다. 철학적 질문과 답을 따라가며 사고가 확장됩니다. 입문서로 매우 좋은 책입니다.",
        "연금술사": "파울로 코엘료가 꿈과 운명, 자기 발견의 여정을 아름답게 그려냅니다. 간결한 문장과 깊은 메시지가 인상적입니다. 읽고 나면 용기를 얻을 수 있습니다.",
        "오만과 편견": "제인 오스틴이 사랑과 계급, 인간관계를 섬세하게 묘사합니다. 엘리자베스와 다아시의 관계가 매력적입니다. 시대를 초월한 로맨스입니다.",
        "제인 에어": "샬럿 브론테가 여성의 독립과 자아실현을 강인하게 그려냅니다. 제인의 성장과 사랑이 감동적입니다. 고전문학의 대표작입니다.",
        "폭풍의 언덕": "에밀리 브론테가 사랑과 복수, 인간의 본성을 격렬하게 묘사합니다. 히스클리프와 캐서린의 관계가 강렬합니다. 읽고 나면 깊은 여운이 남습니다.",
        "위대한 유산": "찰스 디킨스가 성장과 사회적 계급, 인간의 선과 악을 그려냅니다. 피프의 인생 여정이 흥미롭습니다. 고전문학의 매력을 느낄 수 있습니다.",
        "오페라의 유령": "가스통 르루가 미스터리와 로맨스를 오페라 하우스라는 공간에서 펼칩니다. 유령의 슬픔과 사랑이 인상적입니다. 극적인 전개가 돋보입니다.",
        "레미제라블": "빅토르 위고가 인간의 구원과 사랑, 사회적 정의를 웅장하게 그려냅니다. 장발장의 삶과 용기가 감동을 줍니다. 프랑스 문학의 걸작입니다.",
    }
    
    conditions = ["new", "like_new", "very_good", "good", "acceptable"]
    trade_statuses = ["available", "available", "available", "available", "available", "available", "pending", "not_available"]
    
    book_copies = []
    publications = []
    
    # Track used ISBNs to avoid duplicates
    used_isbns = set()
    
    publication_cache = {}
    isbn_cache = {}
    for i in range(count):
        owner = random.choice(users)
        book_info = random.choice(books_data)
        title = book_info["title"]
        author_name = book_info["author"]
        # Find author object
        author_obj = None
        for a in authors:
            if a.name == author_name:
                author_obj = a
                break
        pub_key = (title, author_name)
        if pub_key in publication_cache:
            publication = publication_cache[pub_key]
        else:
            # Generate unique ISBN for each publication
            if pub_key in isbn_cache:
                isbn_13 = isbn_cache[pub_key]
            else:
                isbn_13 = f"978{random.randint(1000000000, 9999999999)}"
                isbn_cache[pub_key] = isbn_13
            # 책별 상세 설명 우선, 없으면 일반 설명
            description = descriptions_by_book.get(title, random.choice(descriptions_general))
            publication = BookPublication.objects.create(
                title=title,
                isbn_13=isbn_13,
                subtitle="",
                publisher=random.choice(publishers),
                publication_date=random_date_in_past(3650).date(),
                pages=random.randint(150, 600),
                language=random.choice(["Korean", "English"]),
                description=description,
            )
            if author_obj:
                publication.authors.set([author_obj])
            publication.genres.set(random.sample(genres, k=random.randint(1, 3)))
            publications.append(publication)
            publication_cache[pub_key] = publication
        # Create user's copy of the publication
        book_copy = BookCopy.objects.create(
            publication=publication,
            owner=owner,
            condition=random.choice(conditions),
            trade_status=random.choice(trade_statuses),
            owner_notes=random.choice(["깨끗한 상태입니다", "밑줄 조금 있어요", "상태 좋아요", ""]),
            is_for_barter=random.choice([True, True, True, True, True, False]),
        )
        book_copies.append(book_copy)
    
    print(f"  Created {len(publications)} unique publications and {len(book_copies)} book copies")
    return book_copies

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
        "읽는 내내 즐거웠어요",
        "책을 덮고도 여운이 남아요",
        "삶에 대한 생각이 바뀌었어요",
        "가볍게 읽기 좋은 책",
        "휴식에 딱 맞는 책",
        "친구에게 꼭 추천하고 싶어요",
        "감동과 재미를 모두 잡은 작품",
    ]

    review_contents_general = [
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
        "읽으면서 마음이 따뜻해졌어요.",
        "현실을 돌아보게 하는 책입니다.",
        "읽고 나서 오랫동안 기억에 남아요.",
        "삶에 대한 새로운 시각을 얻었습니다.",
        "가볍게 읽기 좋은 책이에요.",
        "휴식 시간에 딱 맞는 책입니다.",
        "감동과 재미를 모두 잡은 작품입니다.",
        "친구에게 꼭 추천하고 싶어요.",
        "스토리 전개가 흥미진진합니다.",
        "문장 하나하나가 인상적입니다.",
    ]

    review_contents_by_book = {
        "데미안": "싱클레어의 내면적 성장과 갈등이 섬세하게 그려져 감동적입니다. 자기 자신을 돌아보게 만드는 힘이 있습니다. 읽고 나면 오랫동안 여운이 남습니다.",
        "사피엔스": "인류의 기원과 문명의 발전을 흥미롭게 풀어내어 지적 호기심을 자극합니다. 복잡한 주제를 쉽게 설명해주어 누구나 읽기 좋습니다. 읽고 나면 세상을 보는 시각이 달라집니다.",
        "1984": "감시와 통제의 사회에서 인간의 자유와 존엄성을 고민하게 만듭니다. 전체주의의 위험을 생생하게 느끼게 해줍니다. 현실을 다시 바라보게 만드는 소설입니다.",
        "채식주의자": "인간의 내면과 사회적 억압을 섬세하게 표현합니다. 불편함과 아름다움이 공존하는 독특한 분위기가 인상적입니다. 읽는 내내 강렬한 메시지가 남습니다.",
        "코스모스": "우주에 대한 경이로움과 과학적 사실이 어우러져 있습니다. 칼 세이건의 설명이 친절하고 흥미롭습니다. 읽고 나면 세상을 더 넓게 바라보게 됩니다.",
        "부의 추월차선": "경제적 자유를 얻는 방법을 현실적으로 제시합니다. 기존의 부에 대한 관념을 뒤집는 통찰이 가득합니다. 실천적인 조언이 많아 동기부여가 됩니다.",
        "숨결이 바람 될 때": "삶과 죽음에 대한 진솔한 고백이 깊은 울림을 줍니다. 의사이자 환자로서의 경험이 인상적입니다. 인생의 의미를 다시 생각하게 만드는 책입니다.",
        "불편한 편의점": "따뜻한 인간미와 소소한 일상이 담겨 있습니다. 편의점에서 펼쳐지는 다양한 이야기가 공감됩니다. 읽고 나면 마음이 편안해집니다.",
        "어떻게 살 것인가": "인생에 대한 철학적 성찰이 담긴 에세이입니다. 삶의 방향성과 가치에 대해 깊이 고민하게 만듭니다. 현실적인 조언과 따뜻한 위로가 있습니다.",
        "해리포터와 마법사의 돌": "마법과 우정, 용기가 어우러진 흥미진진한 이야기입니다. 해리포터의 세계에 빠져들게 만듭니다. 어린이와 어른 모두에게 사랑받는 작품입니다.",
        "위대한 개츠비": "미국의 꿈과 허상, 그리고 사랑의 비극이 담겨 있습니다. 화려함 뒤에 숨겨진 인간의 외로움이 인상적입니다. 시대를 초월한 고전입니다.",
        "이방인": "주인공 뫼르소의 무감각함이 독특하게 다가옵니다. 삶과 죽음, 사회적 규범에 대해 생각하게 합니다. 인간 존재에 대한 탐구가 돋보입니다.",
        "노인과 바다": "노인의 끈기와 용기가 감동을 줍니다. 인간과 자연, 도전의 의미를 다시 생각하게 합니다. 간결한 문체 속에 깊은 의미가 숨어 있습니다.",
        "호밀밭의 파수꾼": "홀든의 솔직한 시선과 내면의 혼란이 공감됩니다. 성장통을 겪는 모든 이에게 추천합니다. 청춘의 방황을 섬세하게 그려낸 소설입니다.",
        "동물농장": "동물들의 혁명과 그 이후의 변화가 인간 사회를 반영합니다. 짧지만 강렬한 메시지를 전달합니다. 풍자와 사회 비판이 돋보이는 작품입니다.",
        "멋진 신세계": "인간의 자유와 행복, 기술의 발전에 대해 고민하게 만듭니다. 미래 사회에 대한 비판적 시각이 담겨 있습니다. 읽고 나면 많은 생각이 남는 책입니다.",
        "시간의 역사": "우주의 기원과 구조를 쉽게 설명합니다. 복잡한 과학 이론을 친절하게 풀어줍니다. 과학에 관심 있는 독자에게 추천합니다.",
        "총균쇠": "인류 문명의 발전을 총, 균, 쇠라는 관점에서 분석합니다. 방대한 자료와 논리가 인상적입니다. 역사와 과학을 함께 즐길 수 있습니다.",
        "정의란 무엇인가": "정의와 도덕, 사회적 가치에 대해 깊이 있게 탐구합니다. 다양한 사례와 토론이 흥미롭습니다. 생각할 거리를 많이 주는 책입니다.",
        "생각의 탄생": "창의성과 사고의 과정을 다양한 예시로 설명합니다. 창의적 사고를 키우고 싶은 사람에게 추천합니다. 읽고 나면 새로운 시각을 얻게 됩니다.",
        "지적 대화를 위한 넓고 얕은 지식": "복잡한 사회, 역사, 철학을 쉽게 풀어줍니다. 다양한 분야를 한 권에 담아내어 입문서로 좋습니다. 지적 호기심을 자극하는 책입니다.",
        "미움받을 용기": "아들러 심리학을 바탕으로 용기와 자기 수용을 이야기합니다. 삶의 태도를 바꾸고 싶은 사람에게 추천합니다. 읽고 나면 마음이 가벼워집니다.",
        "아몬드": "감정과 성장, 가족의 의미를 섬세하게 그려냅니다. 주인공의 내면적 변화가 인상적입니다. 따뜻하면서도 슬픈 이야기입니다.",
        "82년생 김지영": "한국 사회의 여성 문제를 현실적으로 그려냅니다. 김지영의 삶을 통해 공감과 성찰을 이끌어냅니다. 사회적 메시지가 강한 소설입니다.",
        "완득이": "청소년의 성장과 가족, 우정의 이야기를 따뜻하게 풀어냅니다. 유쾌하면서도 감동적인 스토리입니다. 읽고 나면 미소가 지어집니다.",
        "살인자의 기억법": "독특한 시점과 심리 묘사로 긴장감을 높입니다. 치매에 걸린 살인자의 내면이 흥미롭게 그려집니다. 마지막까지 눈을 뗄 수 없는 소설입니다.",
        "우리들의 일그러진 영웅": "권력과 인간 심리를 학교라는 공간에서 날카롭게 분석합니다. 짧지만 강렬한 메시지가 있습니다. 한국 현대문학의 대표작입니다.",
        "장미의 이름": "중세 수도원을 배경으로 미스터리와 철학을 결합합니다. 복잡한 플롯과 깊은 사유가 인상적입니다. 지적 호기심을 자극하는 소설입니다.",
        "참을 수 없는 존재의 가벼움": "사랑과 존재, 자유에 대해 철학적으로 탐구합니다. 인물들의 내면적 갈등이 깊이 있게 그려집니다. 읽고 나면 오랫동안 여운이 남습니다.",
        "백년의 고독": "마법적 리얼리즘으로 가족의 역사를 그려냅니다. 환상과 현실이 어우러진 독특한 분위기입니다. 세계문학의 걸작입니다.",
        "죄와 벌": "인간의 죄와 구원, 내면의 갈등을 심도 있게 다룹니다. 라스콜리니코프의 심리 변화가 인상적입니다. 러시아 문학의 정수를 느낄 수 있습니다.",
        "카라마조프가의 형제들": "가족과 신, 인간 본성에 대해 깊이 있게 탐구합니다. 복잡한 인물 관계와 철학적 대화가 돋보입니다. 읽고 나면 많은 생각이 남는 책입니다.",
        "전쟁과 평화": "러시아의 역사와 인간의 삶을 방대한 스케일로 그려냅니다. 사랑과 전쟁, 평화에 대한 깊은 사유가 담겨 있습니다. 고전문학의 진수를 느낄 수 있습니다.",
        "변신": "인간 소외와 불안, 존재의 의미를 독특하게 표현합니다. 주인공 그레고르의 변화가 상징적으로 다가옵니다. 읽고 나면 묘한 여운이 남습니다.",
        "그리스인 조르바": "자유와 삶의 열정을 조르바라는 인물을 통해 보여줍니다. 인생을 즐기는 태도와 철학이 인상적입니다. 읽고 나면 삶에 대한 용기가 생깁니다.",
        "수레바퀴 아래서": "청소년의 성장과 사회적 억압을 섬세하게 그려냅니다. 한스의 내면적 갈등이 공감됩니다. 슬프면서도 아름다운 이야기입니다.",
        "나르치스와 골드문트": "예술과 삶, 사랑에 대한 철학적 사유를 담았습니다. 두 인물의 대조적 삶이 인상적입니다. 깊은 여운을 남기는 소설입니다.",
        "모모": "시간의 소중함과 인간관계를 따뜻하게 그려냅니다. 모모의 순수함이 감동을 줍니다. 어린이와 어른 모두에게 추천합니다.",
        "끝없는 이야기": "상상력과 모험, 성장의 의미를 환상적으로 풀어냅니다. 바스티안의 모험이 흥미진진합니다. 읽고 나면 상상력이 풍부해집니다.",
        "소피의 세계": "철학의 역사를 소피의 시선으로 쉽게 설명합니다. 철학적 질문과 답을 따라가며 사고가 확장됩니다. 입문서로 매우 좋은 책입니다.",
        "연금술사": "꿈과 운명, 자기 발견의 여정을 아름답게 그려냅니다. 간결한 문장과 깊은 메시지가 인상적입니다. 읽고 나면 용기를 얻을 수 있습니다.",
        "오만과 편견": "사랑과 계급, 인간관계를 섬세하게 묘사합니다. 엘리자베스와 다아시의 관계가 매력적입니다. 시대를 초월한 로맨스입니다.",
        "제인 에어": "여성의 독립과 자아실현을 강인하게 그려냅니다. 제인의 성장과 사랑이 감동적입니다. 고전문학의 대표작입니다.",
        "폭풍의 언덕": "사랑과 복수, 인간의 본성을 격렬하게 묘사합니다. 히스클리프와 캐서린의 관계가 강렬합니다. 읽고 나면 깊은 여운이 남습니다.",
        "위대한 유산": "성장과 사회적 계급, 인간의 선과 악을 그려냅니다. 피프의 인생 여정이 흥미롭습니다. 고전문학의 매력을 느낄 수 있습니다.",
        "오페라의 유령": "미스터리와 로맨스를 오페라 하우스라는 공간에서 펼칩니다. 유령의 슬픔과 사랑이 인상적입니다. 극적인 전개가 돋보입니다.",
        "레미제라블": "인간의 구원과 사랑, 사회적 정의를 웅장하게 그려냅니다. 장발장의 삶과 용기가 감동을 줍니다. 프랑스 문학의 걸작입니다.",
    }
    
    reviews = []
    for i in range(count):
        book = random.choice(books)
        reviewer = book.owner  # 반드시 소유자만 리뷰 작성
        # 책별 상세 리뷰 우선, 없으면 일반 리뷰
        review_content = review_contents_by_book.get(book.title, random.choice(review_contents_general))
        review = BookReview.objects.create(
            book=book,
            reviewer=reviewer,
            book_title=book.title,
            author_name=book.author_names,
            rating=random.randint(3, 5),
            title=random.choice(review_titles),
            content=review_content,
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
        "언젠가 꼭 읽어보고 싶어요.",
        "베스트셀러라서 궁금해요.",
        "지인 추천으로 담았어요.",
        "표지가 예뻐서 담았어요.",
        "리뷰가 좋아서 기대돼요.",
        "마음에 들어서 찜했습니다.",
        "새로운 장르에 도전하고 싶어요.",
        "읽고 나서 감상 남기고 싶어요.",
        "시간 날 때 꼭 읽을 거예요.",
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

# def create_collections(users, books):
#     """Create book collections."""
#     print("Creating book collections...")
    
#     collection_names = [
#         "내 인생 책들",
#         "SF 소설 모음",
#         "철학 서적",
#         "읽은 책",
#         "추천 도서",
#         "올해의 책",
#         "My Favorites",
#         "Classic Novels",
#         "Must Read Books",
#     ]
    
#     collections = []
#     for user in random.sample(users, k=min(10, len(users))):
#         # Each selected user has 1-3 collections
#         num_collections = random.randint(1, 3)
        
#         # Shuffle collection names for this user to ensure uniqueness
#         available_names = collection_names.copy()
#         random.shuffle(available_names)
        
#         for i in range(num_collections):
#             # Use index to ensure unique names per user
#             collection_name = available_names[i] if i < len(available_names) else f"컬렉션 {i+1}"
            
#             collection, created = BookCollection.objects.get_or_create(
#                 name=collection_name,
#                 owner=user,
#                 defaults={
#                     "description": f"{user.username}님의 특별한 책 모음",
#                     "is_public": random.choice([True, True, False]),
#                 }
#             )
            
#             if created:
#                 # Add books to collection
#                 num_books = random.randint(3, 8)
#                 collection_books = random.sample(books, min(num_books, len(books)))
#                 collection.books.set(collection_books)
                
#                 collections.append(collection)
    
#     print(f"  Created {len(collections)} book collections")
#     return collections

# def create_reading_statuses(users, books):
#     """Create reading statuses."""
#     print("Creating reading statuses...")
    
#     statuses = ["want_to_read", "currently_reading", "read", "did_not_finish"]
#     notes = [
#         "정말 재미있어요!",
#         "천천히 읽는 중",
#         "완독 목표!",
#         "좋은 책이네요",
#         "",
#     ]
    
#     reading_statuses = []
#     for user in users:
#         # Each user has 5-12 books with reading status
#         num_books = random.randint(5, 12)
#         status_books = random.sample(books, min(num_books, len(books)))
        
#         for book in status_books:
#             status = random.choice(statuses)
            
#             # Get pages from publication
#             pages = book.publication.pages if book.publication.pages else 300
            
#             reading_status = ReadingStatus.objects.create(
#                 user=user,
#                 book=book,
#                 status=status,
#                 pages_read=random.randint(0, pages),
#                 start_date=random_date_in_past(180).date() if status != "want_to_read" else None,
#                 finish_date=random_date_in_past(90).date() if status == "read" else None,
#                 personal_rating=random.randint(3, 5) if status == "read" else None,
#                 notes=random.choice(notes),
#             )
            
#             reading_statuses.append(reading_status)
    
#     print(f"  Created {len(reading_statuses)} reading statuses")
#     return reading_statuses

# def create_barter_requests(users, books):
#     """Create barter requests with new simplified flow: backend auto-selects books."""
#     print("Creating barter requests...")
    
#     message_templates = [
#         "I'd like to offer '{}' for exchange.",
#         "Would you be interested in '{}'?",
#         "This is '{}' from my collection.",
#         "이 책 정말 좋아요! 제 컬렉션에 추가하고 싶습니다.",
#         "깔끔한 상태의 책입니다. 마음에 드셨으면 좋겠어요.",
#         "흥미로운 책이에요. 교환 고려해주세요!",
#     ]
    
#     # Status choices: pending, completed, rejected
#     statuses = ["pending", "pending", "pending", "completed", "rejected"]
    
#     barter_requests = []
#     for _ in range(15):
#         requester = random.choice(users)
#         recipient = random.choice([u for u in users if u != requester])
        
#         # Get books from each user
#         requester_books = list(requester.book_copies.filter(is_for_barter=True, trade_status="available"))
#         recipient_books = list(recipient.book_copies.filter(is_for_barter=True, trade_status="available"))
        
#         # Need at least 1 book from each user
#         if not recipient_books or not requester_books:
#             continue
        
#         status = random.choice(statuses)
#         requested_book = random.choice(recipient_books)
        
#         # Select up to 3 books from requester's available books
#         num_offered = min(3, len(requester_books))
#         offered_books = random.sample(requester_books, num_offered)
        
#         # Generate messages for each offered book
#         messages = []
#         for book in offered_books:
#             template = random.choice(message_templates)
#             messages.append(template.format(book.title) if '{}' in template else template)
        
#         barter = BarterRequest.objects.create(
#             requester=requester,
#             recipient=recipient,
#             requested_book=requested_book,
#             offered_book_ids=[str(book.id) for book in offered_books],
#             message="\n---\n".join(messages),
#             status=status,
#             created_at=random_date_in_past(30),
#         )
        
#         # Update trade_status based on status
#         if status == "pending":
#             # Mark all books as not_available
#             requested_book.trade_status = "not_available"
#             requested_book.save()
#             for book in offered_books:
#                 book.trade_status = "not_available"
#                 book.save()
        
#         elif status == "completed":
#             # One of the offered books was accepted
#             selected_book = random.choice(offered_books)
#             barter.offered_book = selected_book
#             barter.completed_date = random_date_in_past(3)
#             barter.save()
            
#             # Transfer ownership
#             requested_book.owner = requester
#             requested_book.is_for_barter = False
#             requested_book.trade_status = "traded"
#             requested_book.save()
            
#             selected_book.owner = recipient
#             selected_book.is_for_barter = False
#             selected_book.trade_status = "traded"
#             selected_book.save()
            
#             # Restore other non-selected books to available
#             for book in offered_books:
#                 if book.id != selected_book.id:
#                     book.trade_status = "available"
#                     book.save()
        
#         elif status == "rejected":
#             # All books restored to available
#             barter.response_date = random_date_in_past(7)
#             barter.response_message = "죄송하지만 교환이 어려울 것 같습니다."
#             barter.save()
            
#             requested_book.trade_status = "available"
#             requested_book.save()
#             for book in offered_books:
#                 book.trade_status = "available"
#                 book.save()
        
#         barter_requests.append(barter)
    
#     print(f"  Created {len(barter_requests)} barter requests")
#     return barter_requests

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
        # posts = create_posts(users, books, count=40)  # 제거됨
        # create_comments(users, posts, count=50)  # posts가 없으므로 comments도 제거
        
        # Create user book interactions
        create_wishlists(users, books)
        
        # Create barter requests
        # create_barter_requests(users, books)
                
        print("=" * 60)
        print("✅ Dummy data creation completed successfully!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  Users: {User.objects.count()}")
        print(f"  Book Publications: {BookPublication.objects.count()}")
        print(f"  Book Copies: {BookCopy.objects.count()}")
        print(f"  Reviews: {BookReview.objects.count()}")
        #print(f"  Posts: {Post.objects.count()}")
        #print(f"  Comments: {Comment.objects.count()}")
        print(f"  Wishlists: {BookWishlist.objects.count()}")
        # print(f"  Barter Requests: {BarterRequest.objects.count()}")
        print(f"  Follows: {Follow.objects.count()}")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
