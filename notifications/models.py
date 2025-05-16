from django.db import models
from django.contrib.auth.models import User
from browsetask.models import Post


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    task = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)  # Link to task
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To {self.user.username}: {self.message[:50]}"