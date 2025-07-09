from django.urls import path
from .views import ProductListView, ProductDetailView, CartAddView, CartListView, OrderCreateView, OrderListView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('cart/add/', CartAddView.as_view(), name='cart-add'),
    path('cart/', CartListView.as_view(), name='cart-list'),
    path('orders/', OrderCreateView.as_view(), name='order-create'),
    path('my-orders/', OrderListView.as_view(), name='order-list'),
]