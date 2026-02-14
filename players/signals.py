from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from utils.cache import cache_key, invalidate
from utils.cloudinary_service import delete_image
from .models import Player


@receiver(post_save, sender=Player)
def invalidate_player_cache_on_save(sender, instance, **kwargs):
    invalidate(
        cache_key("player_of_the_month"),
        cache_key("featured_players"),
        cache_key("dashboard_stats"),
    )


@receiver(post_delete, sender=Player)
def cleanup_player_on_delete(sender, instance, **kwargs):
    delete_image(instance.image_public_id)
    delete_image(instance.passport_photo_public_id)
    invalidate(
        cache_key("player_of_the_month"),
        cache_key("featured_players"),
        cache_key("dashboard_stats"),
    )
