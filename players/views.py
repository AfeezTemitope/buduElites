from rest_framework import generics, status, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from utils.cache import cached_view, cache_key, invalidate, CACHE_TTL
from utils.permissions import IsAdminUser
from utils.cloudinary_service import upload_image, delete_image
from .models import Player
from .serializers import (
    PlayerPublicSerializer,
    PlayerAdminSerializer,
    PlayerListSerializer,
)


# ═══════════════════════════════════════════════════════════════════
# PUBLIC VIEWS (user-facing frontend)
# ═══════════════════════════════════════════════════════════════════


class PlayerOfTheMonthView(APIView):
    permission_classes = [AllowAny]

    @cached_view(
        key_func=lambda self, req: cache_key("player_of_the_month"),
        timeout=CACHE_TTL["long"],
    )
    def get(self, request):
        player = Player.objects.filter(is_player_of_the_month=True).first()
        if not player:
            return Response(
                {"error": "No Player of the Month found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PlayerPublicSerializer(player).data)


class FeaturedPlayersView(APIView):
    permission_classes = [AllowAny]

    @cached_view(
        key_func=lambda self, req: cache_key("featured_players"),
        timeout=CACHE_TTL["long"],
    )
    def get(self, request):
        players = Player.objects.filter(
            is_player_of_the_month=False, status="active"
        )[:3]
        return Response(PlayerPublicSerializer(players, many=True).data)


# ═══════════════════════════════════════════════════════════════════
# ADMIN VIEWS (admin portal frontend)
# ═══════════════════════════════════════════════════════════════════


class AdminPlayerListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/admin/players/?search=&position=&status=
    POST /api/admin/players/
    """
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "guardian_name", "previous_club"]
    filterset_fields = ["position", "status", "team"]
    ordering_fields = ["name", "created_at", "position"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PlayerAdminSerializer
        return PlayerListSerializer

    def get_queryset(self):
        return Player.objects.all()

    def perform_create(self, serializer):
        player = serializer.save()
        invalidate(
            cache_key("player_of_the_month"),
            cache_key("featured_players"),
            cache_key("admin_players"),
            cache_key("dashboard_stats"),
        )
        return player


class AdminPlayerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/admin/players/<id>/
    PATCH  /api/admin/players/<id>/
    DELETE /api/admin/players/<id>/
    """
    permission_classes = [IsAdminUser]
    serializer_class = PlayerAdminSerializer
    queryset = Player.objects.all()

    def perform_update(self, serializer):
        serializer.save()
        invalidate(
            cache_key("player_of_the_month"),
            cache_key("featured_players"),
            cache_key("admin_players"),
            cache_key("dashboard_stats"),
        )

    def perform_destroy(self, instance):
        # Clean up Cloudinary images
        delete_image(instance.image_public_id)
        delete_image(instance.passport_photo_public_id)
        instance.delete()
        invalidate(
            cache_key("player_of_the_month"),
            cache_key("featured_players"),
            cache_key("admin_players"),
            cache_key("dashboard_stats"),
        )


class AdminPlayerUploadPhotoView(APIView):
    """POST /api/admin/players/<id>/upload-photo/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            player = Player.objects.get(pk=pk)
        except Player.DoesNotExist:
            return Response(
                {"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND
            )

        file = request.FILES.get("file") or request.FILES.get("image")
        if not file:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        field = request.data.get("field", "passport_photo")  # or "image"

        # Delete old image if exists
        if field == "passport_photo":
            delete_image(player.passport_photo_public_id)
        else:
            delete_image(player.image_public_id)

        result = upload_image(file, folder="befa/players")

        if field == "passport_photo":
            player.passport_photo = result["url"]
            player.passport_photo_public_id = result["public_id"]
        else:
            player.image = result["url"]
            player.image_public_id = result["public_id"]

        player.save()
        invalidate(cache_key("player_of_the_month"), cache_key("featured_players"))

        return Response({
            "url": result["url"],
            "public_id": result["public_id"],
            "player": PlayerAdminSerializer(player).data,
        })
