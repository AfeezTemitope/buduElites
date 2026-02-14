from rest_framework import generics, status, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
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


# ═══════════════════ PUBLIC VIEWS ═══════════════════


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
            is_player_of_the_month=False, admission_status="admitted"
        )[:3]
        return Response(PlayerPublicSerializer(players, many=True).data)


# ═══════════════════ ADMIN VIEWS ═══════════════════


class AdminPlayerListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["surname", "other_name", "middle_name", "parent_guardian_name"]
    filterset_fields = ["soccer_position", "admission_status", "team"]
    ordering_fields = ["surname", "created_at", "soccer_position"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PlayerAdminSerializer
        return PlayerListSerializer

    def get_queryset(self):
        return Player.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        invalidate(
            cache_key("player_of_the_month"),
            cache_key("featured_players"),
            cache_key("dashboard_stats"),
            cache_key("recent_players"),
            cache_key("position_breakdown"),
        )


class AdminPlayerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PlayerAdminSerializer
    queryset = Player.objects.all()

    def perform_update(self, serializer):
        serializer.save()
        invalidate(
            cache_key("player_of_the_month"),
            cache_key("featured_players"),
            cache_key("dashboard_stats"),
            cache_key("recent_players"),
        )

    def perform_destroy(self, instance):
        delete_image(instance.player_image_public_id)
        instance.delete()
        invalidate(
            cache_key("player_of_the_month"),
            cache_key("featured_players"),
            cache_key("dashboard_stats"),
            cache_key("recent_players"),
            cache_key("position_breakdown"),
        )


class AdminPlayerUploadPhotoView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            player = Player.objects.get(pk=pk)
        except Player.DoesNotExist:
            return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get("file") or request.FILES.get("image")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Delete old image
        delete_image(player.player_image_public_id)

        result = upload_image(file, folder="befa/players")
        player.player_image = result["url"]
        player.player_image_public_id = result["public_id"]
        player.save()

        invalidate(cache_key("player_of_the_month"), cache_key("featured_players"))

        return Response({
            "url": result["url"],
            "public_id": result["public_id"],
            "player": PlayerAdminSerializer(player).data,
        })
