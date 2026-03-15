from django.contrib import admin
from .models import Receiver, AlertGroup, AlertHistory


@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = ['name', 'receive_type', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['receive_type', 'is_active']
    search_fields = ['name', 'email', 'phone']


@admin.register(AlertGroup)
class AlertGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['receivers']


@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):
    list_display = ['alert_name', 'severity', 'status', 'alert_group', 'fired_at', 'resolved_at']
    list_filter = ['severity', 'status']
    search_fields = ['alert_name', 'message']