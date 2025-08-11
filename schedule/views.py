from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from utils.cache import cached_response
from .models import Event
from .serializers import EventSerializer
from django.core.cache import cache
from rest_framework.response import Response

class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.order_by('date')

    @cached_response(
        cache_key_func=lambda self, req: 'event_list',
        timeout=60*15
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)