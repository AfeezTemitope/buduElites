from django.db import models


class Player(models.Model):
    """
    Player model serving both frontends:
    - Public: name, position, team, image, stats, bio, achievements
    - Admin: full registration data (dob, guardian, medical, etc.)
    """

    # ─── Basic Info ──────────────────────────────────────────
    name = models.CharField(max_length=100, db_index=True)
    position = models.CharField(max_length=50, db_index=True)
    team = models.CharField(max_length=100, db_index=True)

    # ─── Registration Info (Admin portal) ────────────────────
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, default="")
    nationality = models.CharField(max_length=50, blank=True, default="")
    state_of_origin = models.CharField(max_length=50, blank=True, default="")
    address = models.TextField(blank=True, default="")

    # ─── Guardian / Emergency ────────────────────────────────
    guardian_name = models.CharField(max_length=100, blank=True, default="")
    guardian_phone = models.CharField(max_length=20, blank=True, default="")
    guardian_email = models.EmailField(blank=True, default="")
    guardian_relationship = models.CharField(max_length=50, blank=True, default="")
    emergency_contact_name = models.CharField(max_length=100, blank=True, default="")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, default="")

    # ─── Medical ─────────────────────────────────────────────
    blood_group = models.CharField(max_length=10, blank=True, default="")
    genotype = models.CharField(max_length=10, blank=True, default="")
    medical_conditions = models.TextField(blank=True, default="")
    allergies = models.TextField(blank=True, default="")

    # ─── Football Info ───────────────────────────────────────
    preferred_foot = models.CharField(max_length=10, blank=True, default="")
    jersey_number = models.IntegerField(blank=True, null=True)
    previous_club = models.CharField(max_length=100, blank=True, default="")
    year_joined = models.IntegerField(blank=True, null=True)

    # ─── Image (Cloudinary CDN) ──────────────────────────────
    image = models.URLField(max_length=500, blank=True, default="")
    image_public_id = models.CharField(max_length=200, blank=True, default="")
    passport_photo = models.URLField(max_length=500, blank=True, default="")
    passport_photo_public_id = models.CharField(max_length=200, blank=True, default="")

    # ─── Stats (Public display) ──────────────────────────────
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)
    rating = models.FloatField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    clean_sheets = models.IntegerField(blank=True, null=True)

    # ─── Profile ─────────────────────────────────────────────
    bio = models.TextField(blank=True, default="")
    achievements = models.JSONField(blank=True, null=True)

    # ─── Status ──────────────────────────────────────────────
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("trial", "Trial"),
        ("graduated", "Graduated"),
    ]
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="active", db_index=True
    )
    is_player_of_the_month = models.BooleanField(default=False)

    # ─── Timestamps ──────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"], name="idx_player_name"),
            models.Index(fields=["position"], name="idx_player_position"),
            models.Index(fields=["status"], name="idx_player_status"),
            models.Index(fields=["-created_at"], name="idx_player_created"),
            models.Index(fields=["is_player_of_the_month"], name="idx_player_potm"),
        ]

    def __str__(self):
        return f"{self.name} ({self.position})"
