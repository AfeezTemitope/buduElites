from django.urls import path
from e_commerce.views import (
    AdminProductListCreateView, AdminProductDetailView, AdminProductUploadImageView,
    AdminOrderListView, AdminOrderUpdateView,
)

urlpatterns = [
    path("products/", AdminProductListCreateView.as_view(), name="admin-product-list"),
    path("products/<int:pk>/", AdminProductDetailView.as_view(), name="admin-product-detail"),
    path("products/<int:pk>/upload-image/", AdminProductUploadImageView.as_view(), name="admin-product-upload"),
    path("orders/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("orders/<int:pk>/", AdminOrderUpdateView.as_view(), name="admin-order-update"),
]
