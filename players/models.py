from django.db import models
from cloudinary.models import CloudinaryField

class Player(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    team = models.CharField(max_length=100)
    image = CloudinaryField('image', blank=True, null=True)  # Stores Cloudinary public ID
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0, blank=True)
    saves = models.IntegerField(default=0, blank=True)
    clean_sheets = models.IntegerField(default=0, blank=True, db_column='cleanSheets')
    bio = models.TextField(blank=True)
    is_player_of_the_month = models.BooleanField(default=False)
    achievements = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating']

    def __str__(self):
        return self.name