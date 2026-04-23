from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "first_name", "last_name", "is_active")
    search_fields = ("display_name", "first_name", "last_name")
    list_filter = ("is_active",)