from django.contrib import admin
from django import forms
from .models import Product, Cart, Order
import cloudinary.uploader
from django.core.cache import cache

class ProductAdminForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    in_stock = forms.NullBooleanField(required=False, label='In Stock')  # Allow null
    class Meta:
        model = Product
        fields = ['name', 'price', 'size', 'image', 'description', 'in_stock']
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
        cache.delete('product_list')
        cache.delete(f'product_{instance.id}')
        return instance

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('name', 'size', 'price', 'in_stock', 'created_at')
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

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('user',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'display_products', 'user', 'status', 'created_at')
    list_filter = ('status',)
    def display_products(self, obj):
        return ", ".join([f"{p.name} ({p.size})" for p in obj.products.all()])
    display_products.short_description = 'Products'