from django.urls import path
from content_hub.views import PostListView, PostDetailView, PostLikeView

urlpatterns = [
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:post_id>/like/", PostLikeView.as_view(), name="post-like"),
]
