from rest_framework import serializers
from .models import Profile

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
