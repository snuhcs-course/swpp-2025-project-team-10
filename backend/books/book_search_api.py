from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def book_search(request):
    query = request.query_params.get("q", "").strip()
    if not query:
        return Response({"error": "Missing query parameter 'q'."}, status=status.HTTP_400_BAD_REQUEST)

    books = Book.objects.filter(Q(title__icontains=query) | Q(authors__name__icontains=query)).distinct()

    if books.exists():
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    else:
        return Response(
            {"message": f"Not found '{query}'."},
            status=status.HTTP_404_NOT_FOUND
        )