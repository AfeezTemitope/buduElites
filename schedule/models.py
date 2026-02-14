from django.db import models


class Event(models.Model):
    EVENT_TYPES = [
        ("training", "Training"),
        ("match", "Match"),
        ("meeting", "Meeting"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=200, blank=True, default="")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="training")
    date = models.DateField(db_index=True)
    time = models.TimeField()
    venue = models.CharField(max_length=100)
    jersey_color = models.CharField(max_length=50, blank=True, default="")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date", "time"]
        indexes = [
            models.Index(fields=["date"], name="idx_event_date"),
            models.Index(fields=["event_type"], name="idx_event_type"),
        ]

    def __str__(self):
        return f"{self.title or self.event_type} on {self.date} at {self.time}"
