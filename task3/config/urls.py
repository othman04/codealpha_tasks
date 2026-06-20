from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='projects:dashboard', permanent=False)),
    path('', include('accounts.urls')),
    path('', include('projects.urls')),
    path('', include('tasks.urls')),
    path('', include('notifications.urls')),
]
