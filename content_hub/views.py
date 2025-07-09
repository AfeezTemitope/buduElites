from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.cache import cache
from .models import Post, Comment, PostLike, CommentLike
from .serializers import PostSerializer, CommentSerializer

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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        cache.set(cache_key, serializer.data, timeout=60*15)
        return Response(serializer.data)

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        cache_key = f'post_{self.kwargs["pk"]}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        cache.set(cache_key, serializer.data, timeout=60*15)
        return Response(serializer.data)

class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        # Broadcast to WebSocket group
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        group_name = f'post_{comment.post.id}_comments'
        serializer = CommentSerializer(comment, context={'request': self.request})
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'comment_message',
                'comment': serializer.data
            }
        )

class PostLikeView(generics.CreateAPIView):
    queryset = PostLike.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        user = request.user
        like, created = PostLike.objects.get_or_create(post=post, user=user)
        if not created:
            like.delete()
            return Response({'message': 'Like removed'})
        return Response({'message': 'Like added'})

class CommentLikeView(generics.CreateAPIView):
    queryset = CommentLike.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        comment_id = kwargs.get('comment_id')
        comment = Comment.objects.get(id=comment_id)
        user = request.user
        like, created = CommentLike.objects.get_or_create(comment=comment, user=user)
        if not created:
            like.delete()
            return Response({'message': 'Like removed'})
        return Response({'message': 'Like added'})