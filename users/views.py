from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from users.serializers import UserCreateSerializer

User = get_user_model()

class RegisterUserView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

