from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Event
from .serializers import EventSerializer
from django.core.cache import cache
from rest_framework.response import Response

class EventListView(generics.ListAPIView):
    """
    Returns the latest event (training schedule), cached in Redis.
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only the latest event
        return Event.objects.order_by('-created_at')[:1]

    def get(self, request, *args, **kwargs):
        cache_key = 'event_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cache.set(cache_key, serializer.data, timeout=60*15)
        return Response(serializer.data)