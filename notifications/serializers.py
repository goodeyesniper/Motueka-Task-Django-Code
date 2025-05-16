from rest_framework import serializers
from .models import Notification
from django.contrib.auth.models import User
from browsetask.models import Post


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.CharField()  # Accept username instead of a User object
    task_id = serializers.SerializerMethodField()  # Now using task_id

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


