from django.db import models
import cloudinary

class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    team = models.CharField(max_length=100)
    image = models.URLField(max_length=200, blank=True, null=True)  # Cloudinary URL
    image_public_id = models.CharField(max_length=100, blank=True, null=True)  # Cloudinary public ID
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)
    rating = models.FloatField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    clean_sheets = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    achievements = models.JSONField(blank=True, null=True)  # List of strings
    is_player_of_the_month = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name