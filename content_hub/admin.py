# admin.py
from django import forms
from django.contrib import admin
from .models import Post, PostLike
import cloudinary.uploader
from django.core.cache import cache
from ckeditor.widgets import CKEditorWidget
import bleach

class PostAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditorWidget(config_name='default'),
        help_text="Use formatting tools for rich text. HTML is allowed but will be sanitized."
    )
    image = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['author', 'description', 'image']

    def clean_description(self):
        raw = self.cleaned_data['description']
        # Allow safe tags
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'a', 'blockquote'
        ]
        allowed_attrs = {
            'a': ['href', 'target', 'rel']
        }
        clean = bleach.clean(
            raw,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
        return clean

    def save(self, commit=True):
        instance = super().save(commit=False)
        image = self.cleaned_data.get('image')
        if image:
            try:
                uploaded = cloudinary.uploader.upload(image, format='webp')
                instance.image_url = uploaded['secure_url']
            except Exception as e:
                raise forms.ValidationError(f"Cloudinary upload failed: {str(e)}")
        if commit:
            instance.save()
        cache.delete('post_list')
        return instance