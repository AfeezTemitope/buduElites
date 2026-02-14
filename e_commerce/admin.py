from django.contrib import admin
from .models import Product, Cart, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "size", "price", "in_stock", "created_at")
    search_fields = ("name",)
    list_filter = ("in_stock",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity", "created_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status",)
