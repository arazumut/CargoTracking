from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Shipment
from vehicle.models import Vehicle, Driver
from tracking.models import Tracking
from django.shortcuts import get_object_or_404

class ShipmentCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        shipment = Shipment.objects.create(
            sender_name=data.get('sender_name'),
            sender_address=data.get('sender_address'),
            sender_phone=data.get('sender_phone'),
            receiver_name=data.get('receiver_name'),
            receiver_address=data.get('receiver_address'),
            receiver_phone=data.get('receiver_phone'),
            description=data.get('description', ''),
            estimated_delivery=data.get('estimated_delivery'),
            shipment_type=data.get('shipment_type'),
            weight_kg=data.get('weight_kg'),
            volume_m3=data.get('volume_m3'),
        )
        Tracking.objects.create(shipment=shipment, status='preparing')
        return Response({'tracking_number': shipment.tracking_number}, status=status.HTTP_201_CREATED)

class ShipmentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shipments = Shipment.objects.all()
        data = [
            {
                'tracking_number': s.tracking_number,
                'sender': s.sender_name,
                'receiver': s.receiver_name,
                'status': s.status,
                'estimated_delivery': s.estimated_delivery,
            } for s in shipments
        ]
        return Response(data)

class ShipmentTrackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, tracking_number):
        shipment = get_object_or_404(Shipment, tracking_number=tracking_number)
        trackings = shipment.trackings.order_by('timestamp')
        history = [
            {'status': t.get_status_display(), 'timestamp': t.timestamp.strftime('%d.%m.%Y %H:%M')} for t in trackings
        ]
        return Response({
            'tracking_number': shipment.tracking_number,
            'status': shipment.get_status_display(),
            'history': history
        })
