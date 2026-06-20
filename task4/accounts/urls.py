from django.urls import path

from .views import UserLoginView, UserLogoutView, register

app_name = "accounts"

urlpatterns = [
  path("login/", UserLoginView.as_view(), name="login"),
  path("register/", register, name="register"),
  path("logout/", UserLogoutView.as_view(), name="logout"),
]
