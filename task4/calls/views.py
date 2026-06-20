from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from chat.models import Room


@login_required
def call_room(request, room_id):
  """Call page — WebRTC signaling added in Version 2/3."""
  room = get_object_or_404(Room, pk=room_id)
  return render(
    request,
    "calls/call.html",
    {"room": room, "call_type": request.GET.get("type", "audio")},
  )
