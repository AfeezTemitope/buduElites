import urllib.parse

from django.conf import settings
from rest_framework import generics, serializers as drf_serializers, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.cache import cached_view, cache_key, invalidate, CACHE_TTL
from utils.permissions import IsAdminUser
from utils.cloudinary_service import upload_image, delete_image
from .models import Product, Cart, Order
from .serializers import (
    ProductSerializer,
    ProductAdminSerializer,
    CartSerializer,
    OrderSerializer,
    OrderAdminSerializer,
)


# ═══════════════════ PUBLIC ═══════════════════


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Product.objects.filter(in_stock=True)

    @cached_view(
        key_func=lambda self, req: cache_key("product_list"),
        timeout=CACHE_TTL["medium"],
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CartAddView(generics.CreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user).select_related("product")


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        product_ids = serializer.validated_data.pop("product_ids")
        products = Product.objects.filter(id__in=product_ids, in_stock=True)
        if not products.exists():
            raise drf_serializers.ValidationError("No valid products found")
        order = serializer.save(user=self.request.user, status="pending")
        order.products.set(products)
        Cart.objects.filter(user=self.request.user).delete()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if settings.WHATSAPP_NUMBER:
            order = Order.objects.get(id=response.data["id"])
            products = order.products.all()
            details = ", ".join([f"{p.name} ({p.size}) - ₦{p.price}" for p in products])
            msg = f"New Order: {details}, User: {order.user.email}"
            response.data["whatsapp_url"] = (
                f"https://wa.me/{settings.WHATSAPP_NUMBER}?text={urllib.parse.quote(msg)}"
            )
        return Response(response.data)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("products")


# ═══════════════════ ADMIN ═══════════════════


class AdminProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductAdminSerializer
    queryset = Product.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        invalidate(cache_key("product_list"), cache_key("dashboard_stats"))


class AdminProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ProductAdminSerializer
    queryset = Product.objects.all()

    def perform_update(self, serializer):
        serializer.save()
        invalidate(cache_key("product_list"))

    def perform_destroy(self, instance):
        delete_image(instance.image_public_id)
        instance.delete()
        invalidate(cache_key("product_list"), cache_key("dashboard_stats"))


class AdminProductUploadImageView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get("file") or request.FILES.get("image")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        delete_image(product.image_public_id)
        result = upload_image(file, folder="befa/products")
        product.image_url = result["url"]
        product.image_public_id = result["public_id"]
        product.save()
        invalidate(cache_key("product_list"))
        return Response({"url": result["url"], "public_id": result["public_id"]})


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderAdminSerializer
    queryset = Order.objects.prefetch_related("products").all()


class AdminOrderUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderAdminSerializer
    queryset = Order.objects.all()
