from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "team", "status", "is_player_of_the_month", "created_at")
    list_filter = ("status", "position", "team", "is_player_of_the_month")
    search_fields = ("name", "guardian_name")
    ordering = ("-created_at",)
