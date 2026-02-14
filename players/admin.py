from django.contrib import admin
from .models import Player


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("surname", "other_name", "soccer_position", "admission_status", "is_player_of_the_month", "created_at")
    list_filter = ("admission_status", "soccer_position", "is_player_of_the_month")
    search_fields = ("surname", "other_name", "parent_guardian_name")
    ordering = ("-created_at",)
