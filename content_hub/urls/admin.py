from django.urls import path
from content_hub.views import AdminPostListCreateView, AdminPostDetailView, AdminPostUploadImageView

urlpatterns = [
    path("posts/", AdminPostListCreateView.as_view(), name="admin-post-list"),
    path("posts/<int:pk>/", AdminPostDetailView.as_view(), name="admin-post-detail"),
    path("posts/<int:pk>/upload-image/", AdminPostUploadImageView.as_view(), name="admin-post-upload"),
]
