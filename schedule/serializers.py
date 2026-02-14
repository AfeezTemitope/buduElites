from rest_framework import serializers
from .models import Event


class EventPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "title", "event_type", "date", "time", "venue", "jersey_color", "created_at"]


class EventAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
