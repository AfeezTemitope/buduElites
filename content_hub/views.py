from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.cache import cache
from .models import Post, PostLike
from .serializers import PostSerializer

class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        cache.delete('post_list')

    def get(self, request, *args, **kwargs):
        cache_key = 'post_list'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True, context={'request': request})
            cache.set(cache_key, serializer.data, timeout=60*15)
            return Response(serializer.data)
        except Exception:
            return Response([])

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cache_key = f'post_{self.kwargs["pk"]}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, context={'request': request})
            cache.set(cache_key, serializer.data, timeout=60*15)
            return Response(serializer.data)
        except Exception:
            return Response({})

class PostLikeView(generics.CreateAPIView):
    queryset = PostLike.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            post_id = kwargs.get('post_id')
            post = Post.objects.get(id=post_id)
            user = request.user
            like, created = PostLike.objects.get_or_create(post=post, user=user)
            cache.delete('post_list')
            cache.delete(f'post_{post_id}')
            if not created:
                like.delete()
                return Response({'message': 'Like removed'})
            return Response({'message': 'Like added'})
        except Exception:
            return Response({'message': 'Error processing like'})