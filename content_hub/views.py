from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.cache import cached_view, cache_key, invalidate, CACHE_TTL
from utils.permissions import IsAdminUser
from utils.cloudinary_service import upload_image, delete_image
from .models import Post, PostLike
from .serializers import PostPublicSerializer, PostAdminSerializer


# ═══════════════════ PUBLIC VIEWS ═══════════════════


class PostListView(generics.ListAPIView):
    serializer_class = PostPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.filter(is_published=True).select_related("author")

    @cached_view(
        key_func=lambda self, req: cache_key("post_list"),
        timeout=CACHE_TTL["medium"],
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.select_related("author")
    serializer_class = PostPublicSerializer
    permission_classes = [AllowAny]


class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            message = "Like removed"
        else:
            message = "Like added"

        invalidate(cache_key("post_list"))
        post.refresh_from_db()
        serializer = PostPublicSerializer(post, context={"request": request})
        return Response({"message": message, "post": serializer.data})


# ═══════════════════ ADMIN VIEWS ═══════════════════


class AdminPostListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/admin/posts/  — list all posts for admin
    POST /api/admin/posts/  — create new post
    """
    permission_classes = [IsAdminUser]
    serializer_class = PostAdminSerializer
    queryset = Post.objects.select_related("author").all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        invalidate(cache_key("post_list"))


class AdminPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PostAdminSerializer
    queryset = Post.objects.all()

    def perform_update(self, serializer):
        serializer.save()
        invalidate(cache_key("post_list"))

    def perform_destroy(self, instance):
        delete_image(instance.image_public_id)
        instance.delete()
        invalidate(cache_key("post_list"))


class AdminPostUploadImageView(APIView):
    """POST /api/admin/posts/<id>/upload-image/"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        file = request.FILES.get("file") or request.FILES.get("image")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        delete_image(post.image_public_id)
        result = upload_image(file, folder="befa/posts")
        post.image_url = result["url"]
        post.image_public_id = result["public_id"]
        post.save()
        invalidate(cache_key("post_list"))

        return Response({"url": result["url"], "public_id": result["public_id"]})
