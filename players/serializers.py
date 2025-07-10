from rest_framework import serializers
from .models import Player
import cloudinary

class PlayerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = [
            'id', 'name', 'position', 'team', 'image', 'goals', 'assists',
            'matches', 'rating', 'saves', 'clean_sheets', 'bio', 'achievements',
            'is_player_of_the_month'
        ]

    def get_image(self, obj):
        if obj.image:
            return cloudinary.CloudinaryImage(obj.image.public_id).build_url(secure=True)
        return '/placeholder.svg'