from django.urls import path
from . import views

urlpatterns = [
    path('post/<int:post_id>/like/', views.toggle_like_view, name='toggle_like'),
    path('post/<int:post_id>/comment/', views.add_comment_view, name='add_comment'),
    path('follow/<str:username>/', views.toggle_follow_view, name='toggle_follow'),
]
