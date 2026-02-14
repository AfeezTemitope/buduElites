from django.db import models
from users.models import User


class Post(models.Model):
    """News/blog post created by admin, consumed by user frontend."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, default="")
    image_public_id = models.CharField(max_length=200, blank=True, default="")
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"], name="idx_post_created"),
            models.Index(fields=["is_published"], name="idx_post_published"),
        ]

    def __str__(self):
        return self.title or f"Post by {self.author.email}"


class PostLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")

    def __str__(self):
        return f"{self.user.email} liked Post {self.post.id}"
