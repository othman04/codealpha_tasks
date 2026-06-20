from django.conf import settings
from django.db import models


class Room(models.Model):
  name = models.CharField(max_length=100)
  created_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="rooms_created",
  )
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]

  def __str__(self):
    return self.name


class Message(models.Model):
  room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages")
  sender = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="messages_sent",
  )
  content = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["created_at"]

  def __str__(self):
    return f"{self.sender.username}: {self.content[:50]}"


class File(models.Model):
  """Shared file model — used in Version 2."""

  room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="files")
  sender = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="files_sent",
  )
  file = models.FileField(upload_to="uploads/%Y/%m/")
  created_at = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ["-created_at"]

  def __str__(self):
    return self.file.name

  @property
  def filename(self):
    import os
    return os.path.basename(self.file.name)
