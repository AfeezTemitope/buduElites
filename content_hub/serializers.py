from rest_framework import serializers
from .models import Post, PostLike
from users.serializers import UserSerializer


class PostPublicSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "author", "title", "description", "image_url",
            "created_at", "updated_at", "like_count", "is_liked",
        ]

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        user = self.context.get("request", {})
        if hasattr(user, "user") and user.user.is_authenticated:
            return obj.likes.filter(user=user.user).exists()
        return False


class PostAdminSerializer(serializers.ModelSerializer):
    author_email = serializers.CharField(source="author.email", read_only=True)
    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "author", "author_email", "title", "description",
            "image_url", "image_public_id", "is_published",
            "created_at", "updated_at", "like_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_like_count(self, obj):
        return obj.likes.count()
