from django.urls import path

from .views import (CreateNotification, MarkNotificationRead, DeleteNotificationById,
                    UserNotificationList, delete_notification_by_user_and_task)

app_name = "notifications"

urlpatterns = [
    path('', UserNotificationList.as_view(), name='user-notifications'),  # GET Notifications
    path('create/', CreateNotification.as_view(), name='create-notification'),  # POST Notifications
    path('delete/', delete_notification_by_user_and_task, name='delete-notification-by-user-task'),
    path('<int:pk>/read/', MarkNotificationRead.as_view(), name='mark-notification-read'),  # Mark Read
    path('<int:pk>/delete/', DeleteNotificationById.as_view(), name='delete-notification-by-id'),  # DELETE Notifications

]