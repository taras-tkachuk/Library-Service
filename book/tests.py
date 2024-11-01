from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from book.models import Book
from book.serializers import BookSerializer


BOOKS_URL = reverse("book:book-list")


class PublicBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

        self.book1 = Book.objects.create(
            title="Test Title",
            author="Test Author",
            cover="Hard",
            inventory=2,
            daily_fee=2.1
        )
        self.book2 = Book.objects.create(
            title="Test Title2",
            author="Test Author2",
            cover="Hard",
            inventory=2,
            daily_fee=2.5
        )

    def test_str_book_method(self) -> None:
        book = Book.objects.first()

        self.assertEqual(str(book), f"{book.title} by {book.author}")

    def test_retrieve_book_detail(self) -> None:
        url = reverse("book:book-detail", args=[self.book1.id])
        res = self.client.get(url)

        serializer = BookSerializer(self.book1)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_create_book_not_allowed(self) -> None:
        data = {
            "title": "New Book",
            "author": "New Author",
            "inventory": 2,
            "daily_fee": 2.5,
        }
        res = self.client.post(BOOKS_URL, data)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_book_not_allowed(self) -> None:
        url = reverse("book:book-detail", args=[self.book1.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "Testpassword123@"
        )
        self.client.force_authenticate(self.user)

        self.book1 = Book.objects.create(
            title="Test Title",
            author="Test Author",
            cover="Hard",
            inventory=2,
            daily_fee=2.1
        )

    def test_create_book_forbidden(self) -> None:
        data = {
            "title": "New Book",
            "author": "New Author",
            "inventory": 2,
            "daily_fee": 2.5,
        }
        res = self.client.post(BOOKS_URL, data)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_book_forbidden(self) -> None:
        url = reverse("book:book-detail", args=[self.book1.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserBookApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "Testpassword123@", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.book1 = Book.objects.create(
            title="Test Title",
            author="Test Author",
            cover="Hard",
            inventory=2,
            daily_fee=2.1
        )

    def test_update_book(self) -> None:
        payload = {
            "title": "New Book",
            "author": "New Author",
            "daily_fee": 2.5,
        }
        url = reverse("book:book-detail", args=[self.book1.id])
        res = self.client.patch(url, payload)
        book = Book.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

    def test_delete_book(self) -> None:
        url = reverse("book:book-detail", args=[self.book1.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
