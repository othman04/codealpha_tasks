from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@user_passes_test(lambda u: u.is_authenticated)
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user)
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@user_passes_test(lambda u: u.is_authenticated)
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications:list')


@user_passes_test(lambda u: u.is_authenticated)
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:list')
