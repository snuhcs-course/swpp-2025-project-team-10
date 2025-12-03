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
        """Test creating a BookCopy with a new publication using ISBN-13"""
        data = {
            "book_title": "New Book with ISBN-13",
            "book_authors": ["New Author One", "New Author Two"],
            "book_isbn_13": "9780987654321",
            "book_isbn_10": "0987654321",
            "book_publisher": "New Publisher",
            "book_published_date": "2023-05-15",
            "book_description": "A brand new book",
            "is_for_barter": True,
            "owner_notes": "Just bought this"
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookCopy.objects.count(), 1)
        self.assertEqual(BookPublication.objects.count(), 2)  # existing + new
        
        # Check BookPublication was created correctly
        new_publication = BookPublication.objects.get(isbn_13="9780987654321")
        self.assertEqual(new_publication.title, "New Book with ISBN-13")
        self.assertEqual(new_publication.isbn_10, "0987654321")
        self.assertEqual(new_publication.description, "A brand new book")
        self.assertEqual(new_publication.authors.count(), 2)
        self.assertIn("New Author One", 
                      list(new_publication.authors.values_list('name', flat=True)))
        
        # Check Publisher was created
        self.assertTrue(Publisher.objects.filter(name="New Publisher").exists())
        
        # Check BookCopy links to new publication
        book_copy = BookCopy.objects.first()
        self.assertEqual(book_copy.publication, new_publication)
        self.assertEqual(book_copy.owner, self.user)

    def test_create_book_copy_new_publication_without_isbn(self):
        """Test creating a BookCopy with a new publication without ISBN"""
        data = {
            "book_title": "Book Without ISBN",
            "book_authors": ["Unknown Author"],
            "book_publisher": "Small Press",
            "book_description": "A book without ISBN",
            "is_for_barter": False
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookPublication.objects.count(), 2)
        
        new_publication = BookPublication.objects.get(title="Book Without ISBN")
        self.assertIsNone(new_publication.isbn_13)
        self.assertIsNone(new_publication.isbn_10)
        self.assertEqual(new_publication.authors.first().name, "Unknown Author")

    def test_find_existing_publication_by_isbn13(self):
        """Test that existing publication is found by ISBN-13"""
        data = {
            "book_title": "Different Title",  # Different title
            "book_authors": ["Different Author"],
            "book_isbn_13": "9781234567890",  # Same ISBN as existing
            "book_publisher": "Different Publisher"
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Should not create new publication
        self.assertEqual(BookPublication.objects.count(), 1)
        
        book_copy = BookCopy.objects.first()
        self.assertEqual(book_copy.publication, self.existing_publication)

    def test_find_existing_publication_by_isbn10(self):
        """Test that existing publication is found by ISBN-10"""
        data = {
            "book_title": "Different Title",
            "book_authors": ["Different Author"],
            "book_isbn_10": "1234567890",  # Same ISBN-10 as existing
            "book_publisher": "Different Publisher"
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookPublication.objects.count(), 1)
        
        book_copy = BookCopy.objects.first()
        self.assertEqual(book_copy.publication, self.existing_publication)

    def test_find_existing_publication_by_title_case_insensitive(self):
        """Test that existing publication is found by title (case-insensitive)"""
        data = {
            "book_title": "EXISTING BOOK",  # Different case
            "book_authors": ["Some Author"]
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
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("book_title", response.data)

    def test_create_book_copy_with_minimal_data(self):
        """Test creating a book with only required fields"""
        data = {
            "book_title": "Minimal Book"
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        new_publication = BookPublication.objects.get(title="Minimal Book")
        self.assertEqual(new_publication.authors.count(), 0)
        self.assertIsNone(new_publication.publisher)
        self.assertEqual(new_publication.description, "")

    def test_create_multiple_copies_same_publication(self):
        """Test that multiple users can own copies of the same publication"""
        # First user creates book
        data = {
            "book_title": "Popular Book",
            "book_authors": ["Famous Author"],
            "book_isbn_13": "9781111111111"
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
        self.assertEqual(BookPublication.objects.count(), 2)  # 1 existing + 1 new
        self.assertEqual(BookCopy.objects.count(), 2)
        
        publication = BookPublication.objects.get(isbn_13="9781111111111")
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
            "book_title": "Complete Book",
            "book_authors": ["Author Name"],
            "book_isbn_13": "9783333333333",
            "book_publisher": "Publisher",
            "book_published_date": "2023-01-01",
            "book_description": "Description",
            "owner_notes": "My notes"
        }
        
        response = self.client.post('/library/books/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check response has expected fields
        expected_fields = [
            'id', 'title', 'authors', 'authors_display', 'author',
            'publisher_name', 'publication_date', 'isbn', 'description',
            'cover_image', 'coverUrl', 'is_for_barter', 'owner_notes',
            'trade_status', 'owner'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verify data
        self.assertEqual(response.data['title'], "Complete Book")
        self.assertEqual(response.data['authors'], ["Author Name"])
        self.assertEqual(response.data['owner'], 'testuser')
        self.assertEqual(response.data['isbn'], "9783333333333")
        self.assertEqual(response.data['owner_notes'], "My notes")