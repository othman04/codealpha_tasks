import json

from channels.generic.websocket import AsyncWebsocketConsumer

# In-memory stroke storage per room (use Redis/DB in production)
whiteboard_strokes = {}


class WhiteboardConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    self.room_id = str(self.scope["url_route"]["kwargs"]["room_id"])
    self.room_group_name = f"whiteboard_{self.room_id}"
    self.user = self.scope["user"]

    if not self.user.is_authenticated:
      await self.close()
      return

    await self.channel_layer.group_add(self.room_group_name, self.channel_name)
    await self.accept()

    strokes = whiteboard_strokes.get(self.room_id, [])
    await self.send(text_data=json.dumps({"type": "history", "strokes": strokes}))

  async def disconnect(self, close_code):
    if hasattr(self, "room_group_name"):
      await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

  async def receive(self, text_data):
    data = json.loads(text_data)
    msg_type = data.get("type")

    if msg_type == "draw":
      stroke = data.get("stroke")
      if stroke:
        if self.room_id not in whiteboard_strokes:
          whiteboard_strokes[self.room_id] = []
        whiteboard_strokes[self.room_id].append(stroke)
        await self.channel_layer.group_send(
          self.room_group_name,
          {"type": "whiteboard_draw", "stroke": stroke, "sender": self.user.username},
        )

    elif msg_type == "clear":
      whiteboard_strokes[self.room_id] = []
      await self.channel_layer.group_send(
        self.room_group_name,
        {"type": "whiteboard_clear", "sender": self.user.username},
      )

  async def whiteboard_draw(self, event):
    if event["sender"] == self.user.username:
      return
    await self.send(
      text_data=json.dumps({"type": "draw", "stroke": event["stroke"]})
    )

  async def whiteboard_clear(self, event):
    if event["sender"] == self.user.username:
      return
    await self.send(text_data=json.dumps({"type": "clear"}))
