from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from utils.cache import cached_response
from .models import Product, Cart, Order
from .serializers import ProductSerializer, CartSerializer, OrderSerializer
from django.core.cache import cache
from django.conf import settings
import urllib.parse


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    @cached_response(cache_key_func=lambda self, req: 'product_list', timeout=60 * 15)
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cache_key = f'product_{self.kwargs["pk"]}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        cache.set(cache_key, serializer.data, timeout=60 * 15)
        return Response(serializer.data)


class CartAddView(generics.CreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_ids = serializer.validated_data.pop('product_ids')  # Remove product_ids from validated data
        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            raise serializers.ValidationError("No valid products found")
        order = serializer.save(user=self.request.user, status='pending')  # Save without product_ids
        order.products.set(products)  # Set ManyToMany relationship
        Cart.objects.filter(user=self.request.user).delete()
        cache.delete('product_list')

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        order = Order.objects.get(id=response.data['id'])
        products = order.products.all()
        product_details = ", ".join([f"{p.name} ({p.size}) - ₦{p.price}" for p in products])
        whatsapp_message = f"New Order: {product_details}, User: {order.user.email}"
        whatsapp_url = f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={urllib.parse.quote(whatsapp_message)}"
        response.data['whatsapp_url'] = whatsapp_url
        return Response(response.data)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
