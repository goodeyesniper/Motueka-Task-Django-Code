from rest_framework import serializers
from .models import Notification
from django.contrib.auth.models import User


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.CharField()  # Accept username instead of a User object

    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'timestamp']

    def create(self, validated_data):
        username = validated_data.pop("user")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found."})

        return Notification.objects.create(user=user, **validated_data)
