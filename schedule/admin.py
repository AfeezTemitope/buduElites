from django.contrib import admin
from django import forms
from .models import Event
import cloudinary.uploader
from django.core.cache import cache

class EventAdminForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = Event
        fields = ['date', 'time', 'venue', 'jersey_color']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        cache.delete('event_list')
        cache.delete(f'event_{instance.id}')
        return instance

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ('date', 'time', 'venue', 'jersey_color', 'created_at')
    list_filter = ('date',)
    ordering = ('date',)

    def delete_model(self, request, obj):
        cache.delete('event_list')
        cache.delete(f'event_{obj.id}')
        obj.delete()

    def delete_queryset(self, request, queryset):
        cache.delete('event_list')
        for obj in queryset:
            cache.delete(f'event_{obj.id}')
        queryset.delete()