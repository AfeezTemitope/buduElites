from django.contrib import admin
from django.core.cache import cache
from .models import Player
import cloudinary.uploader


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'team', 'is_player_of_the_month', 'rating']
    list_filter = ['is_player_of_the_month', 'team']
    search_fields = ['name', 'position']
    list_editable = ['is_player_of_the_month']
    fieldsets = (
        (None, {
            'fields': ('name', 'position', 'team', 'image', 'is_player_of_the_month')
        }),
        ('Statistics', {
            'fields': ('goals', 'assists', 'matches', 'rating', 'saves', 'clean_sheets')
        }),
        ('Details', {
            'fields': ('bio', 'achievements')
        }),
    )
    actions = ['replace_players_of_the_month']

    def replace_players_of_the_month(self, request, queryset):
        """
        Deletes current Player of the Month and Featured Players, their Cloudinary images,
        and clears cache. Expects queryset to include new players (1 for Player of the Month,
        up to 3 for Featured Players).
        """
        # Validate queryset: 1 Player of the Month, up to 3 Featured Players
        new_player_of_the_month = queryset.filter(is_player_of_the_month=True)
        new_featured_players = queryset.filter(is_player_of_the_month=False)

        if new_player_of_the_month.count() != 1:
            self.message_user(request, "Exactly one player must be marked as Player of the Month.", level='error')
            return
        if new_featured_players.count() > 3:
            self.message_user(request, "Maximum of 3 Featured Players allowed.", level='error')
            return

        # Delete existing Player of the Month
        current_player_of_the_month = Player.objects.filter(is_player_of_the_month=True)
        for player in current_player_of_the_month:
            if player.image:
                cloudinary.uploader.destroy(player.image.public_id)
            player.delete()

        # Delete existing Featured Players (assuming you want to limit to 3 in DB)
        current_featured_players = Player.objects.filter(is_player_of_the_month=False)
        for player in current_featured_players:
            if player.image:
                cloudinary.uploader.destroy(player.image.public_id)
            player.delete()

        # Clear cache
        cache.delete('player_of_the_month')
        cache.delete('featured_players')

        # Save new players (already in queryset, ensure they are not deleted)
        self.message_user(request, "Successfully replaced Player of the Month and Featured Players.", level='success')

    replace_players_of_the_month.short_description = "Replace Player of the Month and Featured Players"