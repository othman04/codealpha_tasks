import json

from channels.generic.websocket import AsyncWebsocketConsumer

# In-memory participant tracking (use Redis in production)
call_participants = {}


class CallSignalingConsumer(AsyncWebsocketConsumer):
  """WebRTC signaling — relays offers, answers, and ICE candidates between peers."""

  async def connect(self):
    self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
    self.room_group_name = f"call_{self.room_id}"
    self.user = self.scope["user"]

    if not self.user.is_authenticated:
      await self.close()
      return

    await self.channel_layer.group_add(self.room_group_name, self.channel_name)
    await self.accept()

    room_key = str(self.room_id)
    if room_key not in call_participants:
      call_participants[room_key] = set()

    existing = [u for u in call_participants[room_key] if u != self.user.username]
    call_participants[room_key].add(self.user.username)

    await self.send(
      text_data=json.dumps({"type": "participants", "users": existing})
    )

    await self.channel_layer.group_send(
      self.room_group_name,
      {
        "type": "signal_message",
        "data": {"type": "join", "sender": self.user.username},
      },
    )

  async def disconnect(self, close_code):
    room_key = str(self.room_id) if hasattr(self, "room_id") else None
    if room_key and room_key in call_participants:
      call_participants[room_key].discard(self.user.username)
      if not call_participants[room_key]:
        del call_participants[room_key]

    if hasattr(self, "room_group_name"):
      await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
      if self.user.is_authenticated:
        await self.channel_layer.group_send(
          self.room_group_name,
          {
            "type": "signal_message",
            "data": {"type": "leave", "sender": self.user.username},
          },
        )

  async def receive(self, text_data):
    data = json.loads(text_data)
    data["sender"] = self.user.username
    await self.channel_layer.group_send(
      self.room_group_name,
      {"type": "signal_message", "data": data},
    )

  async def signal_message(self, event):
    data = event["data"]
    sender = data.get("sender")

    if sender == self.user.username:
      return

    target = data.get("target")
    if target and target != self.user.username:
      return

    await self.send(text_data=json.dumps(data))
