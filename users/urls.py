from django.urls import path
from .views import RegisterView, AdminLoginView, MeView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("admin-login/", AdminLoginView.as_view(), name="admin-login"),
    path("me/", MeView.as_view(), name="me"),
]
