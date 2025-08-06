from django.urls import path
from .views import PlayerOfTheMonthView, FeaturedPlayersView

urlpatterns = [
    path('player-of-the-month/', PlayerOfTheMonthView.as_view(), name='player_of_the_month'),
    path('featured-players/', FeaturedPlayersView.as_view(), name='featured_players'),
]