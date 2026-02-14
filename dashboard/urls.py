from django.urls import path
from .views import DashboardStatsView, RecentPlayersView, PositionBreakdownView

urlpatterns = [
    path("stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("recent-players/", RecentPlayersView.as_view(), name="dashboard-recent"),
    path("position-breakdown/", PositionBreakdownView.as_view(), name="dashboard-positions"),
]
