from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from sorl.thumbnail import ImageField
from cloudinary.models import CloudinaryField

import os

IS_DEVELOPMENT = os.environ.get("DJANGO_ENV") == "development"

# User personal information model
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    image = ImageField(upload_to='profiles', blank=True, null=True) if IS_DEVELOPMENT else CloudinaryField('image')

    last_seen = models.DateTimeField(default=now)

    full_name = models.CharField(max_length=100, default="Anonymous")
    email = models.EmailField(null=True, blank=False)
    date_of_birth = models.DateField(blank=True, null=True, default="2000-01-01")  # Default to a generic DOB
    address = models.TextField(blank=True, null=True, default="Not provided")
    contact_number = models.CharField(max_length=20, blank=True, null=True, default="1234567890")

    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    def update_last_seen(self):
        self.last_seen = now()
        self.save()

    def __str__(self):
            return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Create a new Profile() object when a django user is created."""
    if created:
         Profile.objects.create(user=instance, email=instance.email)
        
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# User personal details model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about_me = models.TextField(blank=True)
    expertise = models.JSONField(default=list)  # Storing as a list
    task_preferences = models.JSONField(default=list)  # Checkboxes

    def __str__(self):
        return self.user.username

# User portfolio model
class Album(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
# Import the correct field types first
if IS_DEVELOPMENT:
    from django.db.models import ImageField
else:
    from cloudinary.models import CloudinaryField

# For local host use this
class AlbumImage(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="images")
    image = ImageField(upload_to="portfolio_images/") if IS_DEVELOPMENT else CloudinaryField('image')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(default=0)  # Example: rating from 1 to 5
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for {self.profile.user.username}"




