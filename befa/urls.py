"""
BEFA URL Configuration

API Gateway pattern: All API endpoints under /api/ prefix.
Two consumer groups:
  - /api/          → Public endpoints (user-facing frontend)
  - /api/admin/    → Admin endpoints (admin portal frontend)
  - /api/auth/     → Authentication (shared by both)
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({"status": "healthy", "service": "BEFA API"})


urlpatterns = [
    # Health check
    path("", health_check, name="root"),
    path("health/", health_check, name="health"),
    # Django admin (for superusers only)
    path("django-admin/", admin.site.urls),
    # Auth — shared by both frontends
    path("api/auth/", include("users.urls")),
    path("api/auth/", include("djoser.urls")),
    path("api/auth/", include("djoser.urls.jwt")),
    # Public API — user-facing frontend
    path("api/players/", include("players.urls.public")),
    path("api/content-hub/", include("content_hub.urls.public")),
    path("api/schedule/", include("schedule.urls.public")),
    path("api/ecommerce/", include("e_commerce.urls.public")),
    # Admin API — admin portal frontend
    path("api/admin/", include("players.urls.admin")),
    path("api/admin/", include("content_hub.urls.admin")),
    path("api/admin/", include("schedule.urls.admin")),
    path("api/admin/", include("e_commerce.urls.admin")),
    path("api/admin/dashboard/", include("dashboard.urls")),
    path("api/admin/uploads/", include("uploads.urls")),
]
