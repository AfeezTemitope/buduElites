from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Player
import cloudinary.uploader

@receiver(post_save, sender=Player)
def invalidate_player_cache_on_save(sender, instance, **kwargs):
    cache.delete('player_of_the_month')
    cache.delete('featured_players')

@receiver(post_delete, sender=Player)
def delete_cloudinary_image_and_cache(sender, instance, **kwargs):
    if instance.image:
        cloudinary.uploader.destroy(instance.image.public_id)
    cache.delete('player_of_the_month')
    cache.delete('featured_players')