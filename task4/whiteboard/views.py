from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from chat.models import Room


@login_required
def whiteboard_room(request, room_id):
  room = get_object_or_404(Room, pk=room_id)
  return render(request, "whiteboard/whiteboard.html", {"room": room})
