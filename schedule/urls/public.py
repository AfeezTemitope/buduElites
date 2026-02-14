from django.urls import path
from schedule.views import EventListView

urlpatterns = [
    path("events/", EventListView.as_view(), name="event-list"),
]
