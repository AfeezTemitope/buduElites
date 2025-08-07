from django.contrib import admin
from django import forms
from django.core.cache import cache
from .models import Player
import cloudinary.uploader


class PlayerAdminForm(forms.ModelForm):
    image = forms.ImageField(required=False, label='Player Image')

    class Meta:
        model = Player
        fields = [
            'name', 'position', 'team', 'image', 'goals', 'assists', 'matches',
            'rating', 'saves', 'clean_sheets', 'bio', 'achievements', 'is_player_of_the_month'
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        image = self.cleaned_data.get('image')
        if image:
            try:
                if instance.image_public_id:
                    cloudinary.uploader.destroy(instance.image_public_id)
                uploaded = cloudinary.uploader.upload(image, format='webp')
                instance.image = uploaded['secure_url']
                instance.image_public_id = uploaded['public_id']
            except Exception as e:
                raise forms.ValidationError(f"Cloudinary upload failed: {str(e)}")
        if commit:
            instance.save()
        cache.delete('player_of_the_month')
        cache.delete('featured_players')
        return instance


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    form = PlayerAdminForm
    list_display = ('name', 'position', 'team', 'is_player_of_the_month', 'rating', 'created_at')
    list_filter = ('is_player_of_the_month', 'team')
    search_fields = ('name', 'position')
    actions = ['set_player_of_the_month', 'set_featured_players']

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'position', 'team', 'image', 'is_player_of_the_month')
        }),
        ('Statistics', {
            'fields': ('goals', 'assists', 'matches', 'rating', 'saves', 'clean_sheets')
        }),
        ('Details', {
            'fields': ('bio', 'achievements')
        }),
    )

    def set_player_of_the_month(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select exactly one player.", level='error')
            return
        player = queryset.first()
        try:
            Player.objects.filter(is_player_of_the_month=True).exclude(id=player.id).update(
                is_player_of_the_month=False)
            player.is_player_of_the_month = True
            player.save()
            cache.delete('player_of_the_month')
            self.message_user(request, f"Set {player.name} as Player of the Month.", level='success')
        except Exception as e:
            self.message_user(request, f"Error: {str(e)}", level='error')

    set_player_of_the_month.short_description = "Set as Player of the Month"

    def set_featured_players(self, request, queryset):
        if queryset.count() > 3:
            self.message_user(request, "Select up to three players.", level='error')
            return
        try:
            current_featured = Player.objects.filter(is_player_of_the_month=False)
            total_featured = current_featured.count() + queryset.count()
            if total_featured > 3:
                excess = total_featured - 3
                for player in current_featured[:excess]:
                    if player.image_public_id:
                        cloudinary.uploader.destroy(player.image_public_id)
                    player.delete()
            for player in queryset:
                player.is_player_of_the_month = False
                player.save()
            cache.delete('featured_players')
            self.message_user(request, f"Set {queryset.count()} Featured Player(s).", level='success')
        except Exception as e:
            self.message_user(request, f"Error: {str(e)}", level='error')

    set_featured_players.short_description = "Set as Featured Players"

    def delete_model(self, request, obj):
        if obj.image_public_id:
            cloudinary.uploader.destroy(obj.image_public_id)
        cache.delete('player_of_the_month')
        cache.delete('featured_players')
        obj.delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if obj.image_public_id:
                cloudinary.uploader.destroy(obj.image_public_id)
        cache.delete('player_of_the_month')
        cache.delete('featured_players')
        queryset.delete()