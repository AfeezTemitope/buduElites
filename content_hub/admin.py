from django.contrib import admin
from django import forms
from .models import Post, Comment, PostLike, CommentLike
import cloudinary.uploader
from django.core.cache import cache

class PostAdminForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = Post
        fields = ['author', 'description', 'image']

    def save(self, commit=True):
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
        cache.delete('post_list')
        return instance

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = ('author', 'description_preview', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('description', 'author__email')

    def description_preview(self, obj):
        return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
    description_preview.short_description = 'Description'

    def delete_model(self, request, obj):
        cache.delete('post_list')
        obj.delete()

    def delete_queryset(self, request, queryset):
        cache.delete('post_list')
        queryset.delete()

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text_preview', 'created_at')
    list_filter = ('post', 'author', 'created_at')
    search_fields = ('text', 'author__email')

    def text_preview(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_preview.short_description = 'Text'

    def delete_model(self, request, obj):
        obj.delete()

    def delete_queryset(self, request, queryset):
        queryset.delete()

@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('post', 'user')

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'created_at')
    list_filter = ('comment', 'user')