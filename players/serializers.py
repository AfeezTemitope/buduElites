from rest_framework import serializers
from .models import Player


class PlayerPublicSerializer(serializers.ModelSerializer):
    """Slim serializer for user-facing frontend (player spotlight)."""
    name = serializers.CharField(source='surname', read_only=True)
    position = serializers.CharField(source='soccer_position', read_only=True)
    image = serializers.URLField(source='player_image', read_only=True)

    class Meta:
        model = Player
        fields = [
            "id", "name", "position", "team", "image", "goals",
            "assists", "matches", "rating", "saves", "clean_sheets",
            "bio", "achievements", "is_player_of_the_month", "created_at",
        ]


class PlayerAdminSerializer(serializers.ModelSerializer):
    """Full serializer for admin portal — all fields exposed."""

    class Meta:
        model = Player
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_weaknesses(self, value):
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Weaknesses must be a list.")
        return value


class PlayerListSerializer(serializers.ModelSerializer):
    """Concise serializer for admin player list table."""

    class Meta:
        model = Player
        fields = [
            "id", "surname", "other_name", "middle_name", "soccer_position",
            "admission_status", "player_image", "state_of_origin",
            "date_of_birth", "created_at",
        ]
