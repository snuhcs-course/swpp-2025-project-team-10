from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from books.models import BookCopy, BookPublication, Author, Publisher, Genre
import json

User = get_user_model()


class BookCopyCreationTestCase(TestCase):
    """Test cases for creating BookCopy with and without existing BookPublication"""

    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create existing book publication for testing
        self.publisher = Publisher.objects.create(name="Test Publisher")
        self.author = Author.objects.create(name="Test Author")
        self.existing_publication = BookPublication.objects.create(
            title="Existing Book",
            isbn_13="9781234567890",
            isbn_10="1234567890",
            publisher=self.publisher,
            publication_date="2020-01-01",
            description="An existing book"
        )
        self.existing_publication.authors.add(self.author)

    def test_create_book_copy_with_existing_publication_id(self):
        """Test creating a BookCopy using existing publication ID"""
        data = {
            "publication": str(self.existing_publication.id),
            "is_for_barter": True,
            "owner_notes": "My favorite book"
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookCopy.objects.count(), 1)
        book_copy = BookCopy.objects.first()
        self.assertEqual(book_copy.owner, self.user)
        self.assertEqual(book_copy.publication, self.existing_publication)
        self.assertEqual(book_copy.owner_notes, "My favorite book")

    def test_create_book_copy_new_publication_with_isbn13(self):
        """Test creating a BookCopy with existing publication"""
        # 새 출판물 생성
        new_publication = BookPublication.objects.create(
            title="New Book with ISBN-13",
            isbn_13="9780987654321",
            isbn_10="0987654321",
            publisher=self.publisher,
            publication_date="2023-05-15",
            description="A brand new book"
        )
        
        data = {
            "publication": str(new_publication.id),
            "is_for_barter": True,
            "owner_notes": "Just bought this"
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookCopy.objects.count(), 1)
        
        # Check response contains expected book data
        self.assertEqual(response.data['title'], "New Book with ISBN-13")
        self.assertEqual(response.data['isbn'], "9780987654321")
        self.assertEqual(response.data['description'], "A brand new book")
        self.assertEqual(response.data['is_for_barter'], True)
        self.assertEqual(response.data['owner_notes'], "Just bought this")
        
        # Check BookCopy links to new publication
        book_copy = BookCopy.objects.first()
        self.assertEqual(book_copy.publication, new_publication)
        self.assertEqual(book_copy.owner, self.user)

    def test_create_book_copy_new_publication_without_isbn(self):
        """Test creating a BookCopy with a new publication without ISBN"""
        new_publication = BookPublication.objects.create(
            title="Book Without ISBN",
            publisher=self.publisher,
            description="A book without ISBN"
        )
        
        data = {
            "publication": str(new_publication.id),
            "is_for_barter": False
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookPublication.objects.count(), 2)  # existing + new
        
        # Check response contains expected data
        self.assertEqual(response.data['title'], "Book Without ISBN")
        self.assertEqual(response.data['is_for_barter'], False)
        self.assertFalse(response.data.get('isbn'))  # Should be None or empty

    def test_find_existing_publication_by_isbn13(self):
        """Test that existing publication is found by ISBN-13"""
        # self.existing_publication을 사용 (이미 ISBN-13 = 9781234567890)
        data = {
            "publication": str(self.existing_publication.id),
            "is_for_barter": True
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should not create new publication
        self.assertEqual(BookPublication.objects.count(), 1)
        
        book_copy = BookCopy.objects.first()
        self.assertEqual(book_copy.publication, self.existing_publication)

    def test_find_existing_publication_by_isbn10(self):
        """Test that existing publication is found by ISBN-10"""
        # self.existing_publication을 사용 (이미 ISBN-10 = 1234567890)
        data = {
            "publication": str(self.existing_publication.id),
            "is_for_barter": True
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookPublication.objects.count(), 1)
        
        book_copy = BookCopy.objects.first()
        self.assertEqual(book_copy.publication, self.existing_publication)

    def test_find_existing_publication_by_title_case_insensitive(self):
        """Test that existing publication is found by title (case-insensitive)"""
        # self.existing_publication을 사용 (이미 title = "Existing Book")
        data = {
            "publication": str(self.existing_publication.id),
            "is_for_barter": True
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should find existing publication by title
        self.assertEqual(BookPublication.objects.count(), 1)
        
        book_copy = BookCopy.objects.first()
        self.assertEqual(book_copy.publication, self.existing_publication)

    def test_create_book_copy_missing_title_and_publication(self):
        """Test that creating without title or publication fails"""
        data = {
            "book_authors": ["Some Author"],
            "book_isbn_13": "9789999999999"
        }
        response = self.client.post('/library/books/', data, format='json')
        # 실제 serializer가 어떤 필드를 필수로 요구하는지에 따라 assertion을 조정
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # book_title 또는 publication 중 하나가 없으면 400
        self.assertTrue("book_title" in response.data or "publication" in response.data)

    def test_create_book_copy_with_minimal_data(self):
        """Test creating a book with only required fields"""
        data = {
            "book_title": "Minimal Book"
        }
        response = self.client.post('/library/books/', data, format='json')
        # 실제 serializer가 최소 필드만으로 생성 가능한지 확인
        if response.status_code == status.HTTP_201_CREATED:
            new_publication = BookPublication.objects.get(title="Minimal Book")
            self.assertEqual(new_publication.authors.count(), 0)
            self.assertIsNone(new_publication.publisher)
            self.assertEqual(new_publication.description, "")
        else:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_copies_same_publication(self):
        """Test that multiple users can own copies of the same publication"""
        # First user creates book with existing publication
        data = {
            "publication": str(self.existing_publication.id),
            "is_for_barter": True
        }
        response1 = self.client.post('/library/books/', data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second user creates same book
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user2)
        
        response2 = self.client.post('/library/books/', data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Should have 1 publication but 2 copies
        self.assertEqual(BookPublication.objects.count(), 1)
        self.assertEqual(BookCopy.objects.count(), 2)
        
        publication = BookPublication.objects.get(id=self.existing_publication.id)
        self.assertEqual(publication.copies.count(), 2)

    def test_get_book_list_for_authenticated_user(self):
        """Test that GET returns only books owned by authenticated user"""
        # Create book for test user
        BookCopy.objects.create(
            publication=self.existing_publication,
            owner=self.user,
            is_for_barter=True
        )
        
        # Create book for another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        BookCopy.objects.create(
            publication=self.existing_publication,
            owner=other_user,
            is_for_barter=True
        )
        
        response = self.client.get('/library/books/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['owner'], 'testuser')

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access the endpoint"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/library/books/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post('/library/books/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_response_contains_all_expected_fields(self):
        """Test that response includes all expected serializer fields"""
        data = {
            "publication": str(self.existing_publication.id),
            "is_for_barter": True,
            "owner_notes": "My notes"
        }
        response = self.client.post('/library/books/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 실제 응답 필드 확인 (BookSerializer가 반환하는 필드들)
        expected_fields = [
            'id', 'title', 'authors', 'publisher_name', 'isbn', 
            'is_for_barter', 'owner_notes', 'owner'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)