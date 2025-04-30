from rest_framework import serializers
from .models import Tracking

class TrackingSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Tracking
        fields = ['id', 'shipment', 'status', 'status_display', 'timestamp', 'note']
        
    def get_status_display(self, obj):
        return obj.get_status_display()
