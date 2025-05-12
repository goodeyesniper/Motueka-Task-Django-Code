from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from django.contrib.auth.models import User


class UserNotificationList(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.request.GET.get("username")  # Get username from query params

        if not username:
            return Notification.objects.filter(user=self.request.user).order_by('-timestamp')  # Default to logged-in user
        
        return Notification.objects.filter(user__username=username).order_by('-timestamp')  # Filter by username

class MarkNotificationRead(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if self.get_object().user != self.request.user:
            raise PermissionDenied("You can only update your own notifications.")
        serializer.save(is_read=True)

class CreateNotification(generics.CreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Get username from request data
        username = self.request.data.get("user")

        if not username:
            raise serializers.ValidationError({"error": "Username is required."})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found."})

        # Save notification with associated user
        serializer.save(user=user)

class DeleteNotification(generics.DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        notification_id = kwargs.get("pk")
        try:
            notification = Notification.objects.get(pk=notification_id)

            # Ensure users can only delete their own notifications
            if notification.user != request.user:
                raise PermissionDenied("You can only delete your own notifications.")

            notification.delete()
            return Response({"message": "Notification deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
