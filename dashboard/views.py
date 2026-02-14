"""
Admin Dashboard API — aggregated statistics.
Matches the admin portal frontend's useDashboard hook.
"""
from django.db.models import Count, Avg, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.cache import cached_view, cache_key, CACHE_TTL
from utils.permissions import IsAdminUser
from players.models import Player
from players.serializers import PlayerListSerializer
from content_hub.models import Post
from schedule.models import Event
from e_commerce.models import Order
from users.models import User


class DashboardStatsView(APIView):
    """GET /api/admin/dashboard/stats/"""
    permission_classes = [IsAdminUser]

    @cached_view(
        key_func=lambda self, req: cache_key("dashboard_stats"),
        timeout=CACHE_TTL["short"],
    )
    def get(self, request):
        now = timezone.now()
        thirty_days_ago = now - timezone.timedelta(days=30)

        total_players = Player.objects.count()
        active_players = Player.objects.filter(status="active").count()
        new_this_month = Player.objects.filter(created_at__gte=thirty_days_ago).count()
        avg_rating = Player.objects.filter(rating__isnull=False).aggregate(
            avg=Avg("rating")
        )["avg"]

        return Response({
            "total_players": total_players,
            "active_players": active_players,
            "new_this_month": new_this_month,
            "average_rating": round(avg_rating, 1) if avg_rating else 0,
            "total_posts": Post.objects.count(),
            "total_events": Event.objects.count(),
            "upcoming_events": Event.objects.filter(date__gte=now.date()).count(),
            "total_orders": Order.objects.count(),
            "pending_orders": Order.objects.filter(status="pending").count(),
            "total_users": User.objects.count(),
        })


class RecentPlayersView(APIView):
    """GET /api/admin/dashboard/recent-players/"""
    permission_classes = [IsAdminUser]

    @cached_view(
        key_func=lambda self, req: cache_key("recent_players"),
        timeout=CACHE_TTL["short"],
    )
    def get(self, request):
        players = Player.objects.order_by("-created_at")[:5]
        return Response(PlayerListSerializer(players, many=True).data)


class PositionBreakdownView(APIView):
    """GET /api/admin/dashboard/position-breakdown/"""
    permission_classes = [IsAdminUser]

    @cached_view(
        key_func=lambda self, req: cache_key("position_breakdown"),
        timeout=CACHE_TTL["medium"],
    )
    def get(self, request):
        breakdown = (
            Player.objects.values("position")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        return Response(list(breakdown))
