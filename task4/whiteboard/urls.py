from django.urls import path

from . import views

app_name = "whiteboard"

urlpatterns = [
  path("whiteboard/<int:room_id>/", views.whiteboard_room, name="board"),
]
