from rest_framework import serializers
from .models import Post, Offer
from accounts.serializers import ProfileSerializer
from accounts.models import Profile
from django.contrib.auth.models import User


class OfferSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'message', 'created_at']
        

class PostSerializer(serializers.ModelSerializer):
    author_profile = serializers.SerializerMethodField()
    author_username = serializers.CharField(source='author.username', read_only=True)  # ✅ Add this
    image = serializers.SerializerMethodField()
    offers = OfferSerializer(many=True, read_only=True)  # ✅ Add this line

    # Uncomment this in the future if you want full name
    # author_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'task_title', 'task_details', 'image', 'address', 
            'date', 'time_from', 'time_to', 'budget_option', 'budget_value',
            'created_at', 'status',
            
            'author_profile', 'author_username',
            'offers'  # ✅ Add this

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
            if request:  # ✅ Ensure request exists
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url  # ✅ Return relative URL if request is missing
        
        return None

        
    # def get_image(self, obj):
    #     request = self.context.get('request')
    #     if obj.image and hasattr(obj.image, 'url'):
    #         print("Image URL:", obj.image.url)
    #         return request.build_absolute_uri(obj.image.url)
    #     return None

    
    # Uncomment this too when ready
    # def get_author_full_name(self, obj):
    #     full_name = f"{obj.author.first_name} {obj.author.last_name}".strip()
    #     return full_name if full_name else None