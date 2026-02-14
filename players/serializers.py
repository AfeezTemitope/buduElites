from rest_framework import serializers
from .models import Player


class PlayerPublicSerializer(serializers.ModelSerializer):
    """Slim serializer for the user-facing frontend."""

    class Meta:
        model = Player
        fields = [
            "id", "name", "position", "team", "image", "goals",
            "assists", "matches", "rating", "saves", "clean_sheets",
            "bio", "achievements", "is_player_of_the_month", "created_at",
        ]


class PlayerAdminSerializer(serializers.ModelSerializer):
    """Full serializer for admin portal — all fields exposed."""

    achievements = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Player
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_achievements(self, value):
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Achievements must be a list.")
        return value


class PlayerListSerializer(serializers.ModelSerializer):
    """Concise serializer for admin player list table."""

    class Meta:
        model = Player
        fields = [
            "id", "name", "position", "team", "status", "image",
            "passport_photo", "jersey_number", "age", "created_at",
        ]
