from django.contrib import admin
from django import forms
from .models import Event
import cloudinary.uploader
from django.core.cache import cache

class EventAdminForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = Event
        fields = ['date', 'time', 'venue', 'jersey_color', 'image']

    def save(self, commit=True):
        # Clear existing events before saving new one
        Event.objects.all().delete()
        cache.delete('event_list')
        instance = super().save(commit=False)
        image = self.cleaned_data.get('image')
        if image:
            try:
                uploaded = cloudinary.uploader.upload(image)
                instance.image_url = uploaded['secure_url']
            except Exception as e:
                raise forms.ValidationError(f"Cloudinary upload failed: {str(e)}")
        if commit:
            instance.save()
        cache.delete('event_list')
        return instance

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventAdminForm
    list_display = ('date', 'time', 'venue', 'jersey_color', 'created_at')
    list_filter = ('date',)

    def delete_model(self, request, obj):
        cache.delete('event_list')
        obj.delete()

    def delete_queryset(self, request, queryset):
        cache.delete('event_list')
        queryset.delete()