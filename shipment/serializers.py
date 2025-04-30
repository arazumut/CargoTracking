from rest_framework import serializers
from .models import Shipment
from tracking.models import Tracking

class ShipmentSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    shipment_type_display = serializers.SerializerMethodField()
    vehicle_info = serializers.SerializerMethodField()
    driver_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Shipment
        fields = '__all__'
        read_only_fields = ['tracking_number', 'created_at']
        
    def get_status_display(self, obj):
        return obj.get_status_display()
        
    def get_shipment_type_display(self, obj):
        return obj.get_shipment_type_display()
        
    def get_vehicle_info(self, obj):
        if obj.vehicle:
            return {
                'id': obj.vehicle.id,
                'model': obj.vehicle.model,
                'plate': obj.vehicle.plate
            }
        return None
        
    def get_driver_info(self, obj):
        if obj.driver:
            return {
                'id': obj.driver.id,
                'name': obj.driver.name,
                'phone': obj.driver.phone
            }
        return None

class TrackingHistorySerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Tracking
        fields = ['id', 'status', 'status_display', 'timestamp', 'note']
        
    def get_status_display(self, obj):
        return obj.get_status_display()
