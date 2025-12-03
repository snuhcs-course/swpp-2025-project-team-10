"""
Views for AI-powered book exploration and recommendations.
"""

from ai_integration.services import AIRecommendationService
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def explore_recommendations(request):
    """
    탐색 탭: AI 기반 책 추천.
    
    사용자의 위시리스트와 취향 정보를 바탕으로 추천.
    
    Query Parameters:
        - limit: 추천할 책 개수 (기본 10개)
    
    Returns:
        {
            "recommendations": [
                {
                    "id": "book-uuid",
                    "title": "책 제목",
                    "authors": ["저자1", "저자2"],
                    "genres": ["장르1", "장르2"],
                    "owner": {
                        "id": "user-uuid",
                        "username": "username"
                    },
                    "condition": "good",
                    "cover_image": "url"
                },
                ...
            ]
        }
    """
    limit = int(request.query_params.get('limit', 10))
    
    recommendations = AIRecommendationService.recommend_books_for_exploration(
        user=request.user,
        limit=limit
    )
    
    return Response(recommendations, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_barter_context(request):
    """
    교환 추천 컨텍스트 조회 (디버깅/테스트용).
    
    Request Body:
        {
            "recipient_id": "user-uuid",
            "requested_book_id": "book-uuid"
        }
    
    Returns:
        AI 모델에 전달될 컨텍스트 데이터
    """
    from django.contrib.auth import get_user_model
    from books.models import BookCopy
    
    User = get_user_model()
    
    recipient_id = request.data.get('recipient_id')
    requested_book_id = request.data.get('requested_book_id')
    
    if not recipient_id or not requested_book_id:
        return Response(
            {"error": "recipient_id and requested_book_id are required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        recipient = User.objects.get(pk=recipient_id)
        requested_book = BookCopy.objects.get(pk=requested_book_id)
    except (User.DoesNotExist, BookCopy.DoesNotExist) as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    context_data = AIRecommendationService.get_barter_context_data(
        requester=request.user,
        recipient=recipient,
        requested_book=requested_book
    )
    
    # 표준화된 응답: context, requester_id, recipient_id, requested_book_id
    return Response(
        {
            "context": context_data,
            "requester_id": str(request.user.id),
            "recipient_id": recipient_id,
            "requested_book_id": requested_book_id
        },
        status=status.HTTP_200_OK
    )
