from django.urls import path
from .views import PostListCreateView, PostDetailView, CommentCreateView, PostLikeView, CommentLikeView

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
    path('posts/<int:post_id>/like/', PostLikeView.as_view(), name='post-like'),
    path('comments/<int:comment_id>/like/', CommentLikeView.as_view(), name='comment-like'),
]