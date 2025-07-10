from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from .models import Player
from .serializers import PlayerSerializer


class PlayerOfTheMonthView(APIView):
    permission_classes = [IsAuthenticated]
    CACHE_KEY = 'player_of_the_month'
    CACHE_TIMEOUT = 3600  # 1 hour

    def get(self, request):
        try:
            # Check cache first
            cached_data = cache.get(self.CACHE_KEY)
            if cached_data is not None:
                return Response(cached_data, status=status.HTTP_200_OK)

            # Query database if cache miss
            player = Player.objects.filter(is_player_of_the_month=True).first()
            if not player:
                return Response({"error": "No Player of the Month found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = PlayerSerializer(player)
            data = serializer.data

            # Cache the serialized data
            cache.set(self.CACHE_KEY, data, self.CACHE_TIMEOUT)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_SERVER_ERROR)


class FeaturedPlayersView(APIView):
    permission_classes = [IsAuthenticated]
    CACHE_KEY = 'featured_players'
    CACHE_TIMEOUT = 3600  # 1 hour

    def get(self, request):
        try:
            # Check cache first
            cached_data = cache.get(self.CACHE_KEY)
            if cached_data is not None:
                return Response(cached_data, status=status.HTTP_200_OK)

            # Query database if cache miss
            players = Player.objects.filter(is_player_of_the_month=False)[:3]
            serializer = PlayerSerializer(players, many=True)
            data = serializer.data

            # Cache the serialized data
            cache.set(self.CACHE_KEY, data, self.CACHE_TIMEOUT)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_SERVER_ERROR)