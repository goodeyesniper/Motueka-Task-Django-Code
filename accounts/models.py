from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from sorl.thumbnail import ImageField

from django.utils.timezone import now

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    image = ImageField(upload_to='profiles', blank=True, null=True) # blank=True, null=True OR default='profiles/default.jpg'
    last_seen = models.DateTimeField(default=now)

    full_name = models.CharField(max_length=255, default="Anonymous")
    email = models.EmailField(null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True, default="2000-01-01")  # Default to a generic DOB
    address = models.TextField(blank=True, null=True, default="Not provided")
    contact_number = models.CharField(max_length=10, blank=True, null=True, default="027-339-6384")

    def update_last_seen(self):
        self.last_seen = now()
        self.save()

    def __str__(self):
            return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ Create a new Profile() object when a django user is created."""
    if created:
         Profile.objects.create(user=instance)
        
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


