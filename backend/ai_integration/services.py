"""
AI recommendation services for barter matching and book exploration.
"""
import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Any

from django.conf import settings
from books.models import BookCopy, BookWishlist
from accounts.models import UserTaste
import requests

# Add AI model path to Python path
AI_MODEL_PATH = Path(settings.BASE_DIR).parent / "ai-model" / "src"
if str(AI_MODEL_PATH) not in sys.path:
    sys.path.insert(0, str(AI_MODEL_PATH))

AI_MODEL_BASE_URL = getattr(settings, "AI_MODEL_BASE_URL", os.getenv("AI_MODEL_BASE_URL"))

logger = logging.getLogger(__name__)


class AIRecommendationService:
    """Service for AI-powered book recommendations."""
    
    @staticmethod
    def get_barter_context_data(requester, recipient, requested_book) -> Dict[str, Any]:
        """
        교환 추천을 위한 컨텍스트 데이터 수집.
        
        Args:
            requester: 교환 요청자 (A)
            recipient: 교환 수신자 (B)
            requested_book: B가 요청받은 책
            
        Returns:
            AI 모델에 전달할 컨텍스트 데이터
        """
        # A의 교환 가능한 책들
        requester_available_books = BookCopy.objects.filter(
            owner=requester,
            is_for_barter=True,
            trade_status="available"
        ).select_related('publication').prefetch_related(
            'publication__authors',
            'publication__genres'
        )
        
        # B의 위시리스트
        recipient_wishlist = BookWishlist.objects.filter(
            user=recipient
        ).select_related('book__publication').prefetch_related(
            'book__publication__authors',
            'book__publication__genres'
        )
        
        # B의 취향 정보
        try:
            recipient_taste = UserTaste.objects.get(user=recipient)
        except UserTaste.DoesNotExist:
            recipient_taste = None
                
        # B의 서재 (이미 가지고 있는 책 - 추천에서 제외하기 위해)
        recipient_library = BookCopy.objects.filter(
            owner=recipient
        ).select_related('publication')
        
        return {
            'requester': {
                'id': str(requester.id),
                'username': requester.username,
                'available_books': [
                    {
                        'id': str(book.id),
                        'title': book.publication.title,
                        'authors': [a.name for a in book.publication.authors.all()],
                        'genres': [g.name for g in book.publication.genres.all()],
                        'description': book.publication.description,
                        'condition': book.condition,
                        'pages': book.publication.pages,
                        'language': book.publication.language,
                    }
                    for book in requester_available_books
                ]
            },
            'recipient': {
                'id': str(recipient.id),
                'username': recipient.username,
                'requested_book': {
                    'id': str(requested_book.id),
                    'title': requested_book.publication.title,
                    'authors': [a.name for a in requested_book.publication.authors.all()],
                    'genres': [g.name for g in requested_book.publication.genres.all()],
                },
                'wishlist': [
                    {
                        'id': str(item.book.id),
                        'title': item.book.publication.title,
                        'authors': [a.name for a in item.book.publication.authors.all()],
                        'genres': [g.name for g in item.book.publication.genres.all()],
                        'priority': item.priority,
                        'notes': item.notes,
                    }
                    for item in recipient_wishlist
                ],
                'taste': {
                    'favorite_genres': recipient_taste.favorite_genres if recipient_taste else [],
                    'favorite_authors': recipient_taste.favorite_authors if recipient_taste else [],
                    'favorite_books': recipient_taste.favorite_books if recipient_taste else [],
                    'preferred_length': recipient_taste.preferred_length if recipient_taste else None,
                    'preferred_moods': recipient_taste.preferred_moods if recipient_taste else [],
                    'reading_purposes': recipient_taste.reading_purposes if recipient_taste else [],
                } if recipient_taste else {},
                'owned_book_ids': [str(book.publication_id) for book in recipient_library],
                'owned_book_titles': [book.publication.title for book in recipient_library]
            }
        }
    
    @staticmethod
    def get_exploration_context_data(user) -> Dict[str, Any]:
        """
        탐색 탭 추천을 위한 컨텍스트 데이터 수집.
        
        Args:
            user: 추천을 받을 사용자
            
        Returns:
            AI 모델에 전달할 컨텍스트 데이터
        """
        # 사용자의 위시리스트
        user_wishlist = BookWishlist.objects.filter(
            user=user
        ).select_related('book__publication').prefetch_related(
            'book__publication__authors',
            'book__publication__genres'
        )
        
        # 사용자의 취향 정보
        try:
            user_taste = UserTaste.objects.get(user=user)
        except UserTaste.DoesNotExist:
            user_taste = None
        
        # 사용자의 현재 서재 (이미 가지고 있는 책 - 추천에서 제외하기 위해)
        user_library = BookCopy.objects.filter(
            owner=user
        ).select_related('publication')
        
        return {
            'user': {
                'id': str(user.id),
                'username': user.username,
                'wishlist': [
                    {
                        'id': str(item.book.id),
                        'title': item.book.publication.title,
                        'authors': [a.name for a in item.book.publication.authors.all()],
                        'genres': [g.name for g in item.book.publication.genres.all()],
                        'priority': item.priority,
                        'notes': item.notes,
                    }
                    for item in user_wishlist
                ],
                'taste': {
                    'favorite_genres': user_taste.favorite_genres if user_taste else [],
                    'favorite_authors': user_taste.favorite_authors if user_taste else [],
                    'favorite_books': user_taste.favorite_books if user_taste else [],
                    'preferred_length': user_taste.preferred_length if user_taste else None,
                    'preferred_moods': user_taste.preferred_moods if user_taste else [],
                    'reading_purposes': user_taste.reading_purposes if user_taste else [],
                } if user_taste else {},
                'owned_book_ids': [str(book.id) for book in user_library]
            }
        }
    
    @staticmethod
    def recommend_books_for_barter(requester, recipient, requested_book, limit: int = 3) -> List[Dict[str, Any]]:
        """
        AI를 사용하여 교환에 적합한 책들을 추천.
        가능한 경우 GPU 서버의 AI API를 호출하고, 실패 시 로컬 파이프라인이나 랜덤 선택으로 대체한다.
        """
        context_data = AIRecommendationService.get_barter_context_data(
            requester, recipient, requested_book
        )
        # 1) 원격 GPU 서버의 FastAPI 호출 (multi-book + 이유 포함)
        if AI_MODEL_BASE_URL:
            try:
                remote = AIRecommendationService._call_remote_barter_recommendations(
                    context_data, limit
                )
                if remote:
                    return remote
            except Exception as e:
                logger.exception("Remote AI barter recommendation failed: %s", e)

        # 실제 AI 모델 호출 예시
        try:
            from pipeline.recommender import BarterRecommender
            from data.entities import BarterContext, Item, UserProfile, TradeRequest
            # 컨텍스트 변환 (간단 예시)
            items = {}
            for book in context_data['requester']['available_books']:
                items[book['id']] = Item(
                    item_id=book['id'],
                    owner_id=context_data['requester']['id'],
                    title=book['title'],
                    valuation=1.0,
                    facets={
                        'genre': ','.join(book['genres']),
                        'author': ','.join(book['authors'])
                    },
                    metadata={}
                )
            profiles = {
                context_data['requester']['id']: UserProfile(
                    user_id=context_data['requester']['id'],
                    display_name=context_data['requester']['username'],
                    trust_score=0.8,
                    reliability=0.9,
                    preferences=context_data['recipient']['taste'],
                ),
                context_data['recipient']['id']: UserProfile(
                    user_id=context_data['recipient']['id'],
                    display_name=context_data['recipient']['username'],
                    trust_score=0.8,
                    reliability=0.9,
                    preferences=context_data['recipient']['taste'],
                )
            }
            requests = [
                TradeRequest(
                    user_id=context_data['recipient']['id'],
                    desired_item_ids=[context_data['recipient']['requested_book']['id']],
                    desired_facets={}
                )
            ]
            context = BarterContext(
                items=items,
                profiles=profiles,
                requests=requests
            )
            recommender = BarterRecommender()
            recommendations = recommender.recommend(context, limit=limit)
            return [
                {
                    "id": rec.candidate.item_id,
                    "reason": getattr(rec.negotiation, "rationale", None),
                }
                for rec in recommendations
            ]
        except Exception as e:
            # Log the exception for visibility and debugging
            logger.exception("AI barter recommendation failed: %s", e)
            # 임시: 랜덤으로 선택 (AI 모델 통합 실패 시)
            available_books = BookCopy.objects.filter(
                owner=requester,
                is_for_barter=True,
                trade_status="available"
            ).order_by('?')[:limit]
            return [
                {"id": str(book.id), "reason": None} for book in available_books
            ]

    @staticmethod
    def _call_remote_barter_recommendations(context_data: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Call the GPU-hosted FastAPI to get book ids + reasons."""
        url = f"{AI_MODEL_BASE_URL.rstrip('/')}/api/recommendations/books"
        taste = context_data["recipient"].get("taste", {})

        user_payload = {
            "id": context_data["recipient"]["id"],
            "name": context_data["recipient"]["username"],
            "preferred_genres": taste.get("favorite_genres", []),
            "preferred_moods": taste.get("preferred_moods", []),
            "reading_purposes": taste.get("reading_purposes", []),
            "favorite_authors": taste.get("favorite_authors", []),
            "favorite_books": taste.get("favorite_books", []),
        }

        condition_score_map = {
            "new": 0.95,
            "like_new": 0.9,
            "good": 0.8,
            "fair": 0.6,
            "poor": 0.4,
        }
        candidate_books = []
        for book in context_data["requester"]["available_books"]:
            condition = (book.get("condition") or "").lower()
            candidate_books.append(
                {
                    "id": str(book.get("id")),
                    "title": book.get("title"),
                    "authors": book.get("authors", []),
                    "genres": book.get("genres", []),
                    "moods": [],
                    "popularity": 0.5,
                    "condition_score": condition_score_map.get(condition, 0.7),
                    "metadata": {"description": book.get("description")},
                }
            )

        payload = {
            "user": user_payload,
            "candidate_books": candidate_books,
            "reading_history": context_data["recipient"].get(
                "owned_book_titles", []
            ),
            "max_results": limit,
        }
        response = requests.post(url, json=payload, timeout=8)
        response.raise_for_status()
        data = response.json()
        recommendations = []
        for rec in data.get("recommendations", [])[:limit]:
            if rec.get("id"):
                recommendations.append(
                    {"id": str(rec.get("id")), "reason": rec.get("reason")}
                )
        return recommendations
    
    @staticmethod
    def recommend_books_for_exploration(user, limit: int = 10) -> List[Dict[str, Any]]:
        """
        AI를 사용하여 탐색 탭에서 보여줄 책들을 추천.
        """
        context_data = AIRecommendationService.get_exploration_context_data(user)
        try:
            taste = context_data["user"].get("taste", {})
            favorite_genres = {g.lower() for g in (taste.get("favorite_genres") or [])}
            favorite_authors = {
                a.lower() for a in (taste.get("favorite_authors") or [])
            }

            # 내 서재에 있는 출판물 제외
            owned_publication_ids = set(
                BookCopy.objects.filter(owner=user).values_list(
                    "publication_id", flat=True
                )
            )

            candidates = (
                BookCopy.objects.filter(
                    is_for_barter=True, trade_status="available"
                )
                .exclude(owner=user)
                .exclude(publication_id__in=owned_publication_ids)
                .select_related("publication", "publication__publisher", "owner")
                .prefetch_related("publication__authors", "publication__genres")
            )

            def _score(book: BookCopy) -> float:
                publication = book.publication
                categories = publication.category_scores or []
                top_score = 0.15  # small base so empty scores still rank
                if categories:
                    top_score = max(
                        float(entry.get("score") or 0.0) for entry in categories
                    )

                genre_match = 0.0
                if favorite_genres and categories:
                    genre_hits = [
                        float(entry.get("score") or 0.0)
                        for entry in categories
                        if (entry.get("label") or "").lower() in favorite_genres
                    ]
                    genre_match = max(genre_hits) if genre_hits else 0.0

                author_names = {a.name.lower() for a in publication.authors.all()}
                author_match = 0.2 if favorite_authors & author_names else 0.0

                return top_score + genre_match + author_match

            # 동일한 출판물은 가장 높은 점수를 주는 단일 소유자 선택
            best_per_publication: Dict[str, Dict[str, Any]] = {}
            for book in candidates:
                score = _score(book)
                pub_id = str(book.publication_id)
                current = best_per_publication.get(pub_id)
                if not current or score > current["score"]:
                    best_per_publication[pub_id] = {"book": book, "score": score}

            ranked = sorted(
                best_per_publication.values(),
                key=lambda entry: entry["score"],
                reverse=True,
            )[:limit]

            results: List[Dict[str, Any]] = []
            for entry in ranked:
                book = entry["book"]
                pub = book.publication
                results.append(
                    {
                        "id": str(book.id),
                        "title": pub.title,
                        "authors": [a.name for a in pub.authors.all()],
                        "genres": [g.name for g in pub.genres.all()],
                        "publisher": pub.publisher.name if pub.publisher else None,
                        "isbn": pub.isbn_13 or pub.isbn_10,
                        "owner": {
                            "id": str(book.owner.id),
                            "username": book.owner.username,
                        },
                        "condition": book.condition,
                        "cover_image": pub.cover_image.url
                        if pub.cover_image
                        else None,
                        "score": round(entry["score"], 4),
                    }
                )

            return results
        except Exception as e:
            logger.exception("AI exploration recommendation failed: %s", e)
            return []
