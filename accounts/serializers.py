from rest_framework import serializers
from .models import Album, AlbumImage, Profile, UserProfile, Review
from django.contrib.auth.models import User


class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    about_me = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id',
            'full_name', 
            'email', 
            'date_of_birth',
            'address',
            'contact_number',
            'image_url', 
            'image', 
            'last_seen',
            'about_me',
            'skills',
            'member_since',
            'username',
            'facebook', 'instagram', 'linkedin', 'twitter'
        ]

    def get_image_url(self, obj):
        request = self.context.get('request', None)

        if obj.image and hasattr(obj.image, 'url'):
            image_url = obj.image.url.replace("http://", "https://")  # Force HTTPS

            if request:
                return request.build_absolute_uri(image_url)
            elif image_url:  # Preserve the original fallback
                return image_url

        return None

    # def get_image_url(self, obj):
    #     request = self.context.get('request', None)
    #     if obj.image and request:
    #         return request.build_absolute_uri(obj.image.url)
    #     elif obj.image:
    #         return obj.image.url  # fallback if request is None
    #     return None
    
    def get_about_me(self, obj):
        user_profile = UserProfile.objects.filter(user=obj.user).first()
        return user_profile.about_me if user_profile else "No details provided"

    def get_skills(self, obj):
        user_profile = UserProfile.objects.filter(user=obj.user).first()
        return user_profile.expertise if user_profile else []

    def get_member_since(self, obj):
        return obj.user.date_joined.strftime("%B %Y")

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'about_me', 'expertise', 'task_preferences']
        read_only_fields = ['user']  # So you don’t need to send `user` manually

# class AlbumImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AlbumImage
#         fields = ['id', 'image', 'description', 'uploaded_at']

class AlbumImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        image_field = obj.image

        if image_field and hasattr(image_field, 'url'):
            # Force HTTPS to avoid mixed content warnings
            secure_url = image_field.url.replace("http://", "https://")
            return request.build_absolute_uri(secure_url) if request else secure_url

        return None

    class Meta:
        model = AlbumImage
        fields = ['id', 'image', 'description', 'uploaded_at']


class AlbumSerializer(serializers.ModelSerializer):
    images = AlbumImageSerializer(many=True, read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'created_at', 'images']


class ReviewerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name')
    image = serializers.SerializerMethodField()  # 👈 Change from ImageField to method

    class Meta:
        model = User
        fields = ['username', 'full_name', 'image']

    def get_image(self, obj):
        request = self.context.get('request')
        profile_image = obj.profile.image

        if profile_image and hasattr(profile_image, 'url'):
            secure_url = profile_image.url.replace("http://", "https://")  # Force HTTPS
            return request.build_absolute_uri(secure_url) if request else secure_url

        return None

    # def get_image(self, obj):
    #     request = self.context.get('request')
    #     profile_image = obj.profile.image
    #     if profile_image and hasattr(profile_image, 'url'):
    #         return request.build_absolute_uri(profile_image.url) if request else profile_image.url
    #     return None


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = ReviewerSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['reviewer', 'rating', 'comment', 'created_at']

# class ReviewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Review
#         fields = ['rating', 'comment', 'created_at']  # Remove 'reviewer' and 'profile' from here
