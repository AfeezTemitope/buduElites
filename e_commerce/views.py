from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from django.core.cache import cache
from rest_framework.response import Response

class ProductListView(generics.ListAPIView):
    """
    Lists all products, cached in Redis for faster reloads.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        cache_key = 'product_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*15)
        return Response(serializer.data)

class ProductDetailView(generics.RetrieveAPIView):
    """
    Retrieves a specific product, cached in Redis.
    """
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
        cache.set(cache_key, serializer.data, timeout=60*15)
        return Response(serializer.data)

class OrderCreateView(generics.CreateAPIView):
    """
    Creates a new order with pending status.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='pending')
        cache.delete('product_list')

class OrderListView(generics.ListAPIView):
    """
    Lists orders for the authenticated user only.
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)