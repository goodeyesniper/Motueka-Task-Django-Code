from rest_framework import serializers
from .models import Notification, ChatMessage
from django.contrib.auth.models import User
from browsetask.models import Post


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source='sender.username', read_only=True)
    sender_full_name = serializers.CharField(source='sender.profile.full_name', read_only=True)
    sender_id = serializers.IntegerField(source='sender.id', read_only=True)
    sender_profile_image = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            'id', 'task', 'sender', 'sender_full_name', 'sender_id',
            'sender_profile_image', 'message', 'timestamp', 'is_read'
        ]

    def get_sender_profile_image(self, obj):
        try:
            request = self.context.get('request')
            image = obj.sender.profile.image
            if image:
                return request.build_absolute_uri(image.url) if request else image.url
            return None
        except:
            return None


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    task_id = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'user', 'task_id', 'message', 'is_read', 'timestamp']

    def get_task_id(self, obj):
        return obj.task.id if obj.task else None

    def create(self, validated_data):
        username = validated_data.pop("user")
        task_id = self.initial_data.get("task_id")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found."})

        post = None
        if task_id:
            try:
                post = Post.objects.get(id=task_id)
            except Post.DoesNotExist:
                raise serializers.ValidationError({"error": "Task not found."})

        return Notification.objects.create(user=user, task=post, **validated_data)


