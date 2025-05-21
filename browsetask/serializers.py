from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Offer, Post


class OfferSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    username = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'username', 'full_name', 'message', 'created_at', 'profile_image']

    def get_username(self, obj):
        return obj.user.username  # Fetch username directly from User model

    def get_full_name(self, obj):
        return obj.user.profile.full_name if hasattr(obj.user, "profile") else "Anonymous"  # Fetch from Profile
    
    def get_profile_image(self, obj):
        request = self.context.get('request')  # Get request context
        if obj.user.profile.image and hasattr(obj.user.profile.image, 'url'):
            return request.build_absolute_uri(obj.user.profile.image.url) if request else obj.user.profile.image.url
        return None  # Return None or a default image

class PostSerializer(serializers.ModelSerializer):
    author_profile = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    image = serializers.SerializerMethodField()
    offers = OfferSerializer(many=True, read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)

    author_full_name = serializers.SerializerMethodField()
    assigned_to_full_name = serializers.SerializerMethodField()

    author_profile_image = serializers.SerializerMethodField()
    assigned_to_profile_image = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'task_title', 'task_details', 'image', 'address', 
            'date', 'time_from', 'time_to', 'budget_option', 'budget_value',
            'created_at', 'status',
            
            'author_profile', 'author_username', 'assigned_to',
            'offers',

            'author_full_name', 'assigned_to_full_name',
            'author_profile_image', 'assigned_to_profile_image',
        ]

        # fields = '__all__' # This is an alternative, try this out next time.
    
    def get_author_profile(self, obj):
        request = self.context.get('request')
        try:
            profile = obj.author.profile
            return ProfileSerializer(profile, context={'request': request}).data
        except Profile.DoesNotExist:
            return None
        
    def get_image(self, obj):
        request = self.context.get('request')
        
        if obj.image and hasattr(obj.image, 'url'):
            if request:  # Ensure request exists
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url  # Return relative URL if request is missing
        
        return None
    
    def get_author_full_name(self, obj):
        try:
            return obj.author.profile.full_name
        except Profile.DoesNotExist:
            return obj.author.username  # Fallback if profile doesn't exist

    def get_assigned_to_full_name(self, obj):
        try:
            return obj.assigned_to.profile.full_name if obj.assigned_to else None
        except Profile.DoesNotExist:
            return str(obj.assigned_to) if obj.assigned_to else None
    
    def get_author_profile_image(self, obj):
        request = self.context.get('request')
        try:
            profile_image = obj.author.profile.image
            if profile_image and hasattr(profile_image, 'url'):
                return request.build_absolute_uri(profile_image.url) if request else profile_image.url
        except AttributeError:
            pass
        return None  # Optional: replace with a default image URL if needed

    def get_assigned_to_profile_image(self, obj):
        request = self.context.get('request')
        try:
            profile_image = obj.assigned_to.profile.image
            if profile_image and hasattr(profile_image, 'url'):
                return request.build_absolute_uri(profile_image.url) if request else profile_image.url
        except AttributeError:
            pass
        return None
