from django.contrib import admin
from .models import Notification, ChatMessage

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('user__username', 'message')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'sender', 'message', 'is_read','timestamp')  # Columns to show
    search_fields = ('message', 'sender__username', 'task__task_title')  # Searchable fields
    list_filter = ('timestamp', 'sender')  # Filters on right sidebar
    ordering = ('-timestamp',)  # Order by newest messages first

