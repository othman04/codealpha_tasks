import os

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import File, Message, Room


@login_required
def room_list(request):
  rooms = Room.objects.select_related("created_by").all()
  users = User.objects.exclude(pk=request.user.pk).order_by("username")
  return render(
    request,
    "chat/rooms.html",
    {"rooms": rooms, "users": users},
  )


@login_required
def create_room(request):
  if request.method == "POST":
    name = request.POST.get("name", "").strip()
    if name:
      Room.objects.create(name=name, created_by=request.user)
      messages.success(request, f'Room "{name}" created successfully.')
    else:
      messages.error(request, "Room name cannot be empty.")
  return redirect("chat:rooms")


@login_required
def room_detail(request, room_id):
  room = get_object_or_404(Room, pk=room_id)
  messages_qs = (
    Message.objects.filter(room=room)
    .select_related("sender")
    .order_by("created_at")
  )
  files_qs = (
    File.objects.filter(room=room)
    .select_related("sender")
    .order_by("-created_at")
  )
  users = User.objects.exclude(pk=request.user.pk).order_by("username")
  return render(
    request,
    "chat/room.html",
    {
      "room": room,
      "messages": messages_qs,
      "files": files_qs,
      "users": users,
    },
  )


@login_required
@require_POST
def upload_file(request, room_id):
  room = get_object_or_404(Room, pk=room_id)
  uploaded = request.FILES.get("file")

  if not uploaded:
    return JsonResponse({"error": "No file provided."}, status=400)

  if uploaded.size > settings.MAX_UPLOAD_SIZE:
    return JsonResponse({"error": "File exceeds 10 MB limit."}, status=400)

  shared = File.objects.create(room=room, sender=request.user, file=uploaded)
  filename = os.path.basename(shared.file.name)
  timestamp = shared.created_at.strftime("%H:%M")

  channel_layer = get_channel_layer()
  async_to_sync(channel_layer.group_send)(
    f"chat_{room_id}",
    {
      "type": "file_shared",
      "username": request.user.username,
      "filename": filename,
      "url": shared.file.url,
      "timestamp": timestamp,
    },
  )

  return JsonResponse(
    {
      "filename": filename,
      "url": shared.file.url,
      "username": request.user.username,
      "timestamp": timestamp,
    }
  )
