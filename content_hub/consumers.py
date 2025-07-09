# content_hub/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from users.models import User
from content_hub.models import Comment, Post

logger = logging.getLogger(__name__)


class PostCommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        self.group_name = f'post_{self.post_id}'
        logger.info(f"WebSocket connect attempt for post {self.post_id}, user: {self.scope['user']}")

        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            logger.warning("WebSocket connection rejected: User not authenticated")
            await self.close(code=4001)  # Custom close code for auth failure

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"WebSocket disconnected for post {self.post_id}, code: {close_code}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            post_id = data.get('post')
            text = data.get('text')

            if not post_id or not text:
                await self.send(text_data=json.dumps({'error': 'Invalid data: post and text are required'}))
                return

            logger.info(f"Received message for post {post_id}: {data}")
            logger.info(f"User: {self.scope['user'].email}, Authenticated: {self.scope['user'].is_authenticated}")

            # Create comment
            comment = await self.create_comment(post_id, text, self.scope['user'])
            if comment:
                logger.info(f"Creating comment for post {post_id} by user {self.scope['user'].email}")
                # Broadcast comment to group
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'comment_message',
                        'comment': {
                            'id': comment.id,
                            'post': comment.post_id,
                            'author': {
                                'id': comment.author.id,
                                'email': comment.author.email,
                                'username': comment.author.username,
                            },
                            'text': comment.text,
                            'created_at': comment.created_at.isoformat(),
                            'like_count': 0,
                            'is_liked': False,
                        },
                    }
                )
            else:
                await self.send(text_data=json.dumps(
                    {'error': 'Failed to create comment: Post not found or user not authenticated'}))
        except Exception as e:
            logger.error(f"Error in receive for post {post_id}: {str(e)}")
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def comment_message(self, event):
        # Send comment to WebSocket clients
        await self.send(text_data=json.dumps({'comment': event['comment']}))

    @database_sync_to_async
    def create_comment(self, post_id, text, user):
        if not user.is_authenticated:
            logger.warning("Comment creation failed: User not authenticated")
            return None
        try:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(post=post, author=user, text=text)
            logger.info(f"Comment created: ID {comment.id} for post {post_id}")
            return comment
        except Post.DoesNotExist:
            logger.error(f"Comment creation failed: Post {post_id} does not exist")
            return None
        except Exception as e:
            logger.error(f"Comment creation failed: {str(e)}")
            return None