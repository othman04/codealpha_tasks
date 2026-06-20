from django.contrib import admin

from .models import File, Message, Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
  list_display = ("name", "created_by", "created_at")
  search_fields = ("name", "created_by__username")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
  list_display = ("room", "sender", "content", "created_at")
  list_filter = ("room",)


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
  list_display = ("room", "sender", "file", "created_at")
