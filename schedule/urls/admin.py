from django.urls import path
from schedule.views import AdminEventListCreateView, AdminEventDetailView

urlpatterns = [
    path("events/", AdminEventListCreateView.as_view(), name="admin-event-list"),
    path("events/<int:pk>/", AdminEventDetailView.as_view(), name="admin-event-detail"),
]
