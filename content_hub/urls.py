from django.urls import path
from .views import PostListCreateView, PostDetailView, PostLikeView

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', PostLikeView.as_view(), name='post-like'),

]