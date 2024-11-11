import asyncio
from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from notification.telegram import send_notification
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
        )
        read_only_fields = ("borrow_date", )

    def validate(self, attrs):
        data = super(BorrowingSerializer, self).validate(attrs=attrs)
        attrs["borrow_date"] = datetime.now().date()
        Borrowing.validate_creation_time(
            attrs["borrow_date"], attrs["expected_return_date"], attrs["actual_return_date"],
            ValidationError
        )
        return data

    def create(self, validated_data):
        try:
            with transaction.atomic():
                book = validated_data.pop("book")
                book.rent_book(ValidationError)
                borrowing = Borrowing.objects.create(book=book, **validated_data)
                text = (
                    f"{borrowing.user.email} borrowed "
                    f"{borrowing.book.title}, {borrowing.book.author} "
                    f"till {borrowing.expected_return_date}"
                )
                asyncio.run(send_notification(text))
                return borrowing
        except ValidationError as e:
            raise serializers.ValidationError(str(e))


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "book_title",
            "user_email"
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )
