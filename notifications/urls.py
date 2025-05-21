from django.urls import path

from .views import (CreateNotification, MarkNotificationRead, DeleteNotificationById, ChatView,
                    UserNotificationList, delete_notification_by_user_and_task, mark_all_notifications_read)

app_name = "notifications"

urlpatterns = [
    path('', UserNotificationList.as_view(), name='user-notifications'),  # GET Notifications
    path('create/', CreateNotification.as_view(), name='create-notification'),  # POST Notifications
    path('delete/', delete_notification_by_user_and_task, name='delete-notification-by-user-task'),

    path('<int:pk>/read/', MarkNotificationRead.as_view(), name='mark-notification-read'),  # Mark Read
    path('mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),

    path('<int:pk>/delete/', DeleteNotificationById.as_view(), name='delete-notification-by-id'),  # DELETE Notifications

    path('chat/<int:task_id>/', ChatView.as_view(), name='chat'),
    # path('chat/<int:task_id>/messages/', get_chat_messages, name='chat-messages'),


]