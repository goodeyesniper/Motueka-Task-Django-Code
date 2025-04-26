from rest_framework import serializers
from .models import Profile, UserProfile, Album, AlbumImage


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            'full_name', 
            'email', 
            'date_of_birth',
            'address',
            'contact_number',
            'image_url', 
            'image', 
            'last_seen']  # Add more fields as needed

    def get_image_url(self, obj):
        request = self.context.get('request', None)
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url  # fallback if request is None
        return None

    # def get_image_url(self, obj):
    #     request = self.context.get('request')
    #     if obj.image and hasattr(obj.image, 'url'):
    #         return request.build_absolute_uri(obj.image.url)
    #     return None

## Note: class ProfileSerializer will return something like
# {
#   "image": "profiles/me.jpg",
#   "image_url": "http://127.0.0.1:8000/media/profiles/me.jpg"
# }


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'about_me', 'expertise', 'task_preferences']
        read_only_fields = ['user']  # ✅ So you don’t need to send `user` manually

class AlbumImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumImage
        fields = ['id', 'image', 'description', 'uploaded_at']

class AlbumSerializer(serializers.ModelSerializer):
    images = AlbumImageSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'created_at', 'images']
