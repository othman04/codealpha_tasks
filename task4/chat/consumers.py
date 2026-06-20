import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User

from .models import Message, Room


class ChatConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
    self.room_group_name = f"chat_{self.room_id}"
    self.user = self.scope["user"]

    if not self.user.is_authenticated:
      await self.close()
      return

    room_exists = await self._room_exists(self.room_id)
    if not room_exists:
      await self.close()
      return

    await self.channel_layer.group_add(self.room_group_name, self.channel_name)
    await self.accept()

    await self.channel_layer.group_send(
      self.room_group_name,
      {
        "type": "user_join",
        "username": self.user.username,
      },
    )

  async def disconnect(self, close_code):
    if hasattr(self, "room_group_name"):
      await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
      if self.user.is_authenticated:
        await self.channel_layer.group_send(
          self.room_group_name,
          {
            "type": "user_leave",
            "username": self.user.username,
          },
        )

  async def receive(self, text_data):
    data = json.loads(text_data)
    message_type = data.get("type", "chat_message")

    if message_type == "chat_message":
      content = data.get("message", "").strip()
      if not content:
        return

      saved = await self._save_message(self.room_id, self.user.id, content)
      await self.channel_layer.group_send(
        self.room_group_name,
        {
          "type": "chat_message",
          "message": saved["content"],
          "username": saved["username"],
          "timestamp": saved["timestamp"],
        },
      )

  async def chat_message(self, event):
    await self.send(
      text_data=json.dumps(
        {
          "type": "chat_message",
          "message": event["message"],
          "username": event["username"],
          "timestamp": event["timestamp"],
        }
      )
    )

  async def user_join(self, event):
    await self.send(
      text_data=json.dumps(
        {
          "type": "user_join",
          "username": event["username"],
        }
      )
    )

  async def user_leave(self, event):
    await self.send(
      text_data=json.dumps(
        {
          "type": "user_leave",
          "username": event["username"],
        }
      )
    )

  async def file_shared(self, event):
    await self.send(
      text_data=json.dumps(
        {
          "type": "file_shared",
          "username": event["username"],
          "filename": event["filename"],
          "url": event["url"],
          "timestamp": event["timestamp"],
        }
      )
    )

  @database_sync_to_async
  def _room_exists(self, room_id):
    return Room.objects.filter(pk=room_id).exists()

  @database_sync_to_async
  def _save_message(self, room_id, user_id, content):
    user = User.objects.get(pk=user_id)
    room = Room.objects.get(pk=room_id)
    msg = Message.objects.create(room=room, sender=user, content=content)
    return {
      "content": msg.content,
      "username": user.username,
      "timestamp": msg.created_at.strftime("%H:%M"),
    }


class OnlineUsersConsumer(AsyncWebsocketConsumer):
  """Broadcasts online/offline status across the app."""

  online_group = "online_users"

  async def connect(self):
    self.user = self.scope["user"]
    if not self.user.is_authenticated:
      await self.close()
      return

    await self.channel_layer.group_add(self.online_group, self.channel_name)
    await self.accept()

    online = await self._get_online_usernames()
    await self.send(text_data=json.dumps({"type": "online_list", "users": online}))

    await self.channel_layer.group_send(
      self.online_group,
      {
        "type": "user_online",
        "username": self.user.username,
      },
    )

  async def disconnect(self, close_code):
    if hasattr(self, "user") and self.user.is_authenticated:
      await self.channel_layer.group_discard(self.online_group, self.channel_name)
      await self.channel_layer.group_send(
        self.online_group,
        {
          "type": "user_offline",
          "username": self.user.username,
        },
      )

  async def user_online(self, event):
    await self.send(
      text_data=json.dumps(
        {"type": "user_online", "username": event["username"]}
      )
    )

  async def user_offline(self, event):
    await self.send(
      text_data=json.dumps(
        {"type": "user_offline", "username": event["username"]}
      )
    )

  @database_sync_to_async
  def _get_online_usernames(self):
    return []
