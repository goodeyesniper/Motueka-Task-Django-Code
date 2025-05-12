from django.urls import path

from .views import (CreateNotification, DeleteNotification,
                    MarkNotificationRead, UserNotificationList)

app_name = "notifications"

urlpatterns = [
    path('', UserNotificationList.as_view(), name='user-notifications'),  # GET Notifications
    path('create/', CreateNotification.as_view(), name='create-notification'),  # POST Notifications
    path('<int:pk>/read/', MarkNotificationRead.as_view(), name='mark-notification-read'),  # Mark Read
    path('<int:pk>/delete/', DeleteNotification.as_view(), name='delete-notification'),  # DELETE Notifications

]