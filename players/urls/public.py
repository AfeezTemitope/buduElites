from django.urls import path
from players.views import PlayerOfTheMonthView, FeaturedPlayersView

urlpatterns = [
    path("player-of-the-month/", PlayerOfTheMonthView.as_view(), name="player-of-the-month"),
    path("featured-players/", FeaturedPlayersView.as_view(), name="featured-players"),
]
