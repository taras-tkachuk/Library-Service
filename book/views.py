from rest_framework import viewsets

from book.models import Book
from book.serializers import BookSerializer, BookListSerializer
from library_service.permissions import IsAdminOrIfAuthenticatedReadOnly


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer
