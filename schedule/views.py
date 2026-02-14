from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from utils.cache import cached_view, cache_key, invalidate, CACHE_TTL
from utils.permissions import IsAdminUser
from .models import Event
from .serializers import EventPublicSerializer, EventAdminSerializer


# ═══════════════════ PUBLIC ═══════════════════


class EventListView(generics.ListAPIView):
    serializer_class = EventPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Event.objects.order_by("date", "time")

    @cached_view(
        key_func=lambda self, req: cache_key("event_list"),
        timeout=CACHE_TTL["medium"],
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ═══════════════════ ADMIN ═══════════════════


class AdminEventListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = EventAdminSerializer
    queryset = Event.objects.all()

    def perform_create(self, serializer):
        serializer.save()
        invalidate(cache_key("event_list"), cache_key("dashboard_stats"))


class AdminEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = EventAdminSerializer
    queryset = Event.objects.all()

    def perform_update(self, serializer):
        serializer.save()
        invalidate(cache_key("event_list"))

    def perform_destroy(self, instance):
        instance.delete()
        invalidate(cache_key("event_list"), cache_key("dashboard_stats"))
