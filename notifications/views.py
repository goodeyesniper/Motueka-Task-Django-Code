from .models import Notification
from .serializers import NotificationSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from .models import ChatMessage
from browsetask.models import Post
from .serializers import ChatMessageSerializer

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_chat_messages(request, task_id):
#     messages = ChatMessage.objects.filter(task_id=task_id).order_by('timestamp')
#     serializer = ChatMessageSerializer(messages, many=True, context={'request': request})
#     return Response(serializer.data)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        try:
            task = Post.objects.get(pk=task_id)
            if request.user not in [task.author, task.assigned_to]:
                return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
            messages = ChatMessage.objects.filter(task=task).order_by("timestamp")
            serializer = ChatMessageSerializer(messages, many=True, context={'request': request})

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Post.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, task_id):
        try:
            task = Post.objects.get(pk=task_id)
            if request.user not in [task.author, task.assigned_to]:
                return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
            message = request.data.get("message", "")
            chat_message = ChatMessage.objects.create(task=task, sender=request.user, message=message)

            return Response({
                'message': 'Message sent',
                'data': ChatMessageSerializer(chat_message, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)

        except Post.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


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
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return Response({'status': 'all marked as read'})

class MarkNotificationRead(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # Pass partial=True and supply default data
        instance = self.get_object()

        if instance.user != request.user:
            raise PermissionDenied("You can only update your own notifications.")

        # Only update is_read, we can ignore incoming data
        serializer = self.get_serializer(instance, data={"is_read": True}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


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
