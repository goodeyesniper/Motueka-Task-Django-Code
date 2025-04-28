from rest_framework import serializers
from .models import Profile, UserProfile, Album, AlbumImage

class ProfileSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    about_me = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    member_since = serializers.SerializerMethodField()

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
        ]  # Add more fields as needed

    def get_image_url(self, obj):
        request = self.context.get('request', None)
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url  # fallback if request is None
        return None
    
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
