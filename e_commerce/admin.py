from django.contrib import admin
from django import forms
from .models import Product, Order
import cloudinary.uploader
from django.core.cache import cache

class ProductAdminForm(forms.ModelForm):
    image = forms.ImageField(required=False)

    class Meta:
        model = Product
        fields = ['name', 'price', 'size', 'image', 'description']

    def save(self, commit=True):
        instance = super().save(commit=False)
        image = self.cleaned_data.get('image')
        if image:
            uploaded = cloudinary.uploader.upload(image)
            instance.image_url = uploaded['secure_url']
        if commit:
            instance.save()
        # Clear cache for product list and detail
        cache.delete('product_list')
        cache.delete(f'product_{instance.id}')
        return instance

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'size', 'price', 'created_at')
    search_fields = ('name', 'size')

    def delete_model(self, request, obj):
        cache.delete('product_list')
        cache.delete(f'product_{obj.id}')
        obj.delete()

    def delete_queryset(self, request, queryset):
        cache.delete('product_list')
        for obj in queryset:
            cache.delete(f'product_{obj.id}')
        queryset.delete()

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'status', 'created_at')
    list_filter = ('status',)