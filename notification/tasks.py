from celery import shared_task
import asyncio
from django.utils import timezone
from datetime import timedelta
from borrowing.models import Borrowing
from notification.telegram import send_notification


@shared_task
def check_overdue_borrowings_and_notify() -> None:
    try:
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        overdue_borrowings = Borrowing.objects.select_related("user").filter(
            expected_return_date__lte=tomorrow,
            actual_return_date__isnull=True
        )
        if overdue_borrowings.exists():
            for borrowing in overdue_borrowings:
                message = (f"Borrowing #{borrowing.id} is overdue. "
                           f"Please return the book - {borrowing.book.title}.")
                asyncio.run(send_notification(message))
        else:
            asyncio.run(send_notification("No borrowings overdue today."))
    except Exception as e:
        asyncio.run(send_notification(f"Error in check_overdue_borrowings_and_notify task: {str(e)}"))
