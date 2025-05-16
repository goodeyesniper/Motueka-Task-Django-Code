from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Post(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('closed', 'Closed'),
    ]

    task_title = models.CharField(max_length=50, default="Untitled Task")
    task_details = models.TextField(default="No details provided")
    image = models.ImageField(upload_to='task_images/', blank=True, null=True)
    address = models.CharField(max_length=255, default="No address provided")
    date = models.DateField(default=timezone.now)

    time_from = models.TimeField(default="00:00")
    time_to = models.TimeField(default="23:59")
    budget_option = models.CharField(max_length=20, default='Not sure')
    budget_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp when the task is created

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='open'  # Default to 'open'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # When we delete the user, it will also delete their posts
        default=1  # CHANGE THIS LATER
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_posts'
    )

    def __str__(self):
        return self.task_title[:100]  # Truncating the first 100 characters


class Offer(models.Model):
    post = models.ForeignKey(Post, related_name='offers', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"{self.user.username} offered on {self.post.task_title}"
    
    def __str__(self):
        return f"{self.user.profile.full_name} ({self.user.username}) offered on {self.post.task_title}"
    
    @property
    def profile_image_url(self):
        if self.user.profile.image:  # Ensure user has an image
            return self.user.profile.image.url
        return "/profiles/default.jpg"  # Fallback default image


