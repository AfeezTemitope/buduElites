from django.db import models


class Player(models.Model):
    """
    Player model — fields match the admin portal registration form exactly.
    Field names mirror EMPTY_PLAYER_FORM in the frontend constants.
    """

    # ─── Player Photo (Cloudinary CDN) ───────────────────────
    player_image = models.URLField(max_length=500, blank=True, default="")
    player_image_public_id = models.CharField(max_length=200, blank=True, default="")

    # ─── Parent / Guardian ───────────────────────────────────
    parent_guardian_name = models.CharField(max_length=200, blank=True, default="")
    parent_contact_address = models.TextField(blank=True, default="")
    parent_telephone = models.CharField(max_length=20, blank=True, default="")
    relationship_to_student = models.CharField(max_length=50, blank=True, default="")
    parent_hopes = models.TextField(blank=True, default="")

    # ─── Student / Player Personal Info ──────────────────────
    surname = models.CharField(max_length=100, db_index=True)
    middle_name = models.CharField(max_length=100, blank=True, default="")
    other_name = models.CharField(max_length=100, blank=True, default="")
    contact_address = models.TextField(blank=True, default="")
    state_of_origin = models.CharField(max_length=50, blank=True, default="")
    lga = models.CharField(max_length=100, blank=True, default="")
    nationality = models.CharField(max_length=50, blank=True, default="Nigerian")
    date_of_birth = models.DateField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, default="")
    gender = models.CharField(max_length=20, blank=True, default="")
    weight = models.CharField(max_length=10, blank=True, default="")
    height = models.CharField(max_length=10, blank=True, default="")
    academic_status = models.CharField(max_length=50, blank=True, default="")

    # ─── Football Info ───────────────────────────────────────
    previous_team = models.CharField(max_length=100, blank=True, default="")
    reason_for_leaving = models.CharField(max_length=200, blank=True, default="")
    soccer_position = models.CharField(max_length=50, blank=True, default="", db_index=True)
    player_hopes = models.TextField(blank=True, default="")
    weaknesses = models.JSONField(blank=True, default=list)

    # ─── Medical ─────────────────────────────────────────────
    last_treated_sickness = models.CharField(max_length=200, blank=True, default="")
    blood_group = models.CharField(max_length=10, blank=True, default="")
    genotype = models.CharField(max_length=10, blank=True, default="")
    any_medical_problem = models.BooleanField(default=False)
    medical_problem_details = models.TextField(blank=True, default="")
    currently_on_medication = models.BooleanField(default=False)

    # ─── Office Use ──────────────────────────────────────────
    ADMISSION_CHOICES = [
        ("pending", "Pending"),
        ("admitted", "Admitted"),
        ("not_admitted", "Not Admitted"),
    ]
    admission_status = models.CharField(
        max_length=20, choices=ADMISSION_CHOICES, default="pending", db_index=True
    )
    notes = models.TextField(blank=True, default="")

    # ─── Public Display (user-facing frontend) ───────────────
    # These fields are used by the user-facing frontend for player spotlight
    team = models.CharField(max_length=100, blank=True, default="BEFA")
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    matches = models.IntegerField(default=0)
    rating = models.FloatField(blank=True, null=True)
    saves = models.IntegerField(blank=True, null=True)
    clean_sheets = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, default="")
    achievements = models.JSONField(blank=True, null=True)
    is_player_of_the_month = models.BooleanField(default=False)

    # ─── Timestamps ──────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["surname"], name="idx_player_surname"),
            models.Index(fields=["soccer_position"], name="idx_player_position"),
            models.Index(fields=["admission_status"], name="idx_player_admission"),
            models.Index(fields=["-created_at"], name="idx_player_created"),
            models.Index(fields=["is_player_of_the_month"], name="idx_player_potm"),
        ]

    def __str__(self):
        return f"{self.surname} {self.other_name} ({self.soccer_position})"

    @property
    def name(self):
        """Convenience property for public frontend compatibility."""
        return f"{self.surname} {self.other_name}".strip()

    @property
    def position(self):
        """Alias for public frontend compatibility."""
        return self.soccer_position

    @property
    def image(self):
        """Alias for public frontend compatibility."""
        return self.player_image
