from django.contrib import admin
from .models import Shipment

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['tracking_number', 'sender_name', 'receiver_name', 'status', 'estimated_delivery', 'created_at']
    list_filter = ['status', 'shipment_type', 'created_at']
    search_fields = ['tracking_number', 'sender_name', 'receiver_name', 'receiver_address']
    readonly_fields = ['tracking_number', 'created_at']
