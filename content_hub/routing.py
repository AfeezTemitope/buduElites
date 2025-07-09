from django.urls import re_path

from content_hub import consumers

websocket_urlpatterns = [
    re_path(r'ws/posts/(?P<post_id>\d+)/$', consumers.PostCommentConsumer.as_asgi()),
]