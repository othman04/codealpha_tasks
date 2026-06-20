from django.urls import path

from . import views

app_name = "calls"

urlpatterns = [
  path("call/<int:room_id>/", views.call_room, name="call"),
]
