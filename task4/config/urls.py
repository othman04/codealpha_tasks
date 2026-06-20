from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", lambda request: redirect("accounts:login"), name="home"),
    path("", include("accounts.urls")),
    path("", include("chat.urls")),
    path("", include("calls.urls")),
    path("", include("whiteboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
