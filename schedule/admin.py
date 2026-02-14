from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "date", "time", "venue", "created_at")
    list_filter = ("event_type", "date")
    ordering = ("date",)
