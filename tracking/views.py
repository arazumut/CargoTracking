from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Tracking
from shipment.models import Shipment
from django.shortcuts import get_object_or_404

class TrackingHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, shipment_id):
        shipment = get_object_or_404(Shipment, id=shipment_id)
        trackings = shipment.trackings.order_by('timestamp')
        data = [
            {'status': t.get_status_display(), 'timestamp': t.timestamp.strftime('%d.%m.%Y %H:%M')} for t in trackings
        ]
        return Response(data)

class TrackingStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, shipment_id):
        shipment = get_object_or_404(Shipment, id=shipment_id)
        status_value = request.data.get('status')
        note = request.data.get('note', '')
        if status_value not in dict(Tracking.STATUS_CHOICES):
            return Response({'error': 'Geçersiz durum'}, status=status.HTTP_400_BAD_REQUEST)
        shipment.status = status_value
        shipment.save()
        Tracking.objects.create(shipment=shipment, status=status_value, note=note)
        return Response({'message': 'Durum güncellendi'})
