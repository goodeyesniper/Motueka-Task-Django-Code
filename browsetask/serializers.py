from accounts.models import Profile
from accounts.serializers import ProfileSerializer
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Offer, Post


class OfferSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = ['id', 'user', 'full_name', 'message', 'created_at']

    def get_full_name(self, obj):
        return obj.user.profile.full_name if hasattr(obj.user, "profile") else "Anonymous"  # Fetch from Profile

class PostSerializer(serializers.ModelSerializer):
    author_profile = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)
    image = serializers.SerializerMethodField()
    offers = OfferSerializer(many=True, read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)

    # Uncomment this in the future if you want full name
    # author_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'task_title', 'task_details', 'image', 'address', 
            'date', 'time_from', 'time_to', 'budget_option', 'budget_value',
            'created_at', 'status',
            
            'author_profile', 'author_username', 'assigned_to',
            'offers',  #

            # 'author_full_name',  # ← Uncomment this when ready
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
    
    # Uncomment this too when ready
    # def get_author_full_name(self, obj):
    #     full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
    #     return full_name if full_name else None