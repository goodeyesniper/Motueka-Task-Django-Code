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

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count


from .serializers import ChatMessageSerializer  # make sure this is imported

class UnreadChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            messages = ChatMessage.objects.filter(
                Q(task__author=request.user) | Q(task__assigned_to=request.user),
                ~Q(sender=request.user),
                is_read=False
            ).select_related('sender', 'task', 'sender__profile')

            data = []
            for msg in messages:
                # Use the serializer just for profile image and full name
                serializer = ChatMessageSerializer(msg, context={'request': request})
                serialized = serializer.data

                data.append({
                    'sender_full_name': serialized.get('sender_full_name'),
                    'sender_profile_image': serialized.get('sender_profile_image'),
                    'message': msg.message,
                    'task_id': msg.task.id,
                })

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnreadChatCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = ChatMessage.objects.filter(
            Q(task__author=request.user) | Q(task__assigned_to=request.user),
            ~Q(sender=request.user),
            is_read=False
        ).count()

        return Response({'unread_count': count})
    

class ChatView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, task_id):
        """Retrieve all chat messages for a given task"""
        task = get_object_or_404(Post, pk=task_id)  # Handles errors automatically
        if request.user not in [task.author, task.assigned_to]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        messages = ChatMessage.objects.filter(task=task).order_by("timestamp")
        serializer = ChatMessageSerializer(messages, many=True, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, task_id):
        """Send a message and mark it as unread for the receiver"""
        task = get_object_or_404(Post, pk=task_id)
        if request.user not in [task.author, task.assigned_to]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        message_text = request.data.get("message", "")

        chat_message = ChatMessage.objects.create(
            task=task,
            sender=request.user,
            message=message_text,
            is_read=False  # This ensures only the new message is unread
        )

        return Response({
            'message': 'Message sent',
            'data': ChatMessageSerializer(chat_message, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)

    def patch(self, request, task_id):
        """Mark all messages as read after viewing"""
        task = get_object_or_404(Post, pk=task_id)
        if request.user not in [task.author, task.assigned_to]:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        ChatMessage.objects.filter(task=task, is_read=False).exclude(sender=request.user).update(is_read=True)

        return Response({"status": "All messages marked as read"}, status=status.HTTP_200_OK)


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
