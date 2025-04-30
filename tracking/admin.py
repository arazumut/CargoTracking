from django.contrib import admin
from .models import Tracking

@admin.register(Tracking)
class TrackingAdmin(admin.ModelAdmin):
    list_display = ['shipment', 'status', 'timestamp', 'note']
    list_filter = ['status', 'timestamp']
    search_fields = ['shipment__tracking_number', 'note']
    readonly_fields = ['timestamp']
