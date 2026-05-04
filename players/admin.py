from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "discord_name", "autodarts_name", "is_active", "is_blocked")
    search_fields = ("display_name", "discord_name", "autodarts_name")
    list_filter = ("is_active", "is_blocked")