from .models import Notification


def create_notification(user, message):
    if user:
        Notification.objects.create(user=user, message=message)
