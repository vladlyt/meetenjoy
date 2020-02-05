from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read")
    search_fields = ("user__username", "title")
    list_filter = ("is_read",)
