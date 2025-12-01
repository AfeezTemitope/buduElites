from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from users.serializers import UserCreateSerializer

User = get_user_model()

class RegisterUserView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

from django.http import HttpResponse

def root_view(request):
    return HttpResponse("BEFA API is running!", content_type="text/plain")

