from rest_framework import serializers
from .models import Product, Cart, Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'size', 'image_url', 'description', 'created_at']

class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'product', 'product_id', 'created_at']

class OrderSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    product_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'products', 'product_ids', 'user', 'status', 'created_at']