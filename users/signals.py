import os
import logging

from django.db.models.signals import post_migrate
from django.dispatch import receiver

logger = logging.getLogger("befa.superuser")


@receiver(post_migrate)
def create_superuser_from_env(sender, **kwargs):
    if os.environ.get("ENVIRONMENT") != "production":
        return

    if sender.name != "users":
        return

    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()

    if not all([email, username, password]):
        logger.info("Superuser env vars not set — skipping auto-create.")
        return

    from django.contrib.auth import get_user_model
    User = get_user_model()

    if User.objects.filter(email=email).exists():
        logger.info(f"Superuser {email} already exists — skipping.")
        return

    User.objects.create_superuser(email=email, username=username, password=password)
    logger.info(f"Superuser {email} created successfully.")