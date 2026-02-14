from django.urls import path
from players.views import (
    AdminPlayerListCreateView,
    AdminPlayerDetailView,
    AdminPlayerUploadPhotoView,
)

urlpatterns = [
    path("players/", AdminPlayerListCreateView.as_view(), name="admin-player-list"),
    path("players/<int:pk>/", AdminPlayerDetailView.as_view(), name="admin-player-detail"),
    path("players/<int:pk>/upload-photo/", AdminPlayerUploadPhotoView.as_view(), name="admin-player-upload"),
]
