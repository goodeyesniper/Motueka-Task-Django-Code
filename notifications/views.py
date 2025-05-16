from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification_by_user_and_task(request):
    username = request.query_params.get('username')
    task_id = request.query_params.get('task_id')

    if not username or not task_id:
        return Response({"error": "username and task_id are required"}, status=400)

    try:
        notif = Notification.objects.get(user__username=username, task_id=task_id)
        notif.delete()
        return Response({"success": "Notification deleted."}, status=204)
    except Notification.DoesNotExist:
        return Response({"error": "Notification not found."}, status=404)


class UserNotificationList(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.request.GET.get("username")  # Get username from query params

        if not username:
            return Notification.objects.filter(user=self.request.user).order_by('-timestamp')
        
        return Notification.objects.filter(user__username=username).order_by('-timestamp')

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
        print(">>> DEBUG: Incoming data to CreateNotification:", self.request.data)
        serializer.save()

class DeleteNotificationById(generics.DestroyAPIView):
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
