from django.db import models

class Event(models.Model):
    date = models.DateField()
    time = models.TimeField()
    venue = models.CharField(max_length=100)
    jersey_color = models.CharField(max_length=50)
    image_url = models.URLField(max_length=200, blank=True)  # Optional Cloudinary URL
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Training on {self.date} at {self.time} in {self.venue}"