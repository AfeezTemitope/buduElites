from rest_framework import serializers
from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    image = serializers.URLField(required=False, allow_null=True)
    image_public_id = serializers.CharField(required=False, allow_null=True)
    achievements = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Player
        fields = [
            'id', 'name', 'position', 'team', 'image', 'image_public_id',
            'goals', 'assists', 'matches', 'rating', 'saves', 'clean_sheets',
            'bio', 'achievements', 'is_player_of_the_month', 'created_at'
        ]

    def validate_achievements(self, value):
        if value is not None and not isinstance(value, list):
            raise serializers.ValidationError("Achievements must be a list of strings.")
        return value