from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

from utils.cache import cached_response
from .models import Player
from .serializers import PlayerSerializer


class PlayerOfTheMonthView(APIView):

    @cached_response(
        cache_key_func=lambda self, req: 'player_of_the_month',
        timeout=3600  # 1 hour
    )
    def get(self, request):
        player = Player.objects.filter(is_player_of_the_month=True).first()
        if not player:
            return Response({"error": "No Player of the Month found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlayerSerializer(player)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FeaturedPlayersView(APIView):

    @cached_response(
        cache_key_func=lambda self, req: 'featured_players',
        timeout=3600  # 1 hour
    )
    def get(self, request):
        players = Player.objects.filter(is_player_of_the_month=False)[:3]
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)