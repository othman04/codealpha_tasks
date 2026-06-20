from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
  path("rooms/", views.room_list, name="rooms"),
  path("rooms/create/", views.create_room, name="create_room"),
  path("room/<int:room_id>/", views.room_detail, name="room"),
  path("room/<int:room_id>/upload/", views.upload_file, name="upload_file"),
]
