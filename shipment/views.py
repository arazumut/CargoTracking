from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Shipment
from vehicle.models import Vehicle, Driver
from tracking.models import Tracking
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .serializers import ShipmentSerializer, TrackingHistorySerializer

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
        serializer = ShipmentSerializer(shipment)
        return Response({'tracking_number': shipment.tracking_number, 'shipment': serializer.data}, 
                        status=status.HTTP_201_CREATED)

class ShipmentListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        shipments = Shipment.objects.all().order_by('-created_at')
        
        # Filtreler
        status_filter = request.query_params.get('status', None)
        shipment_type = request.query_params.get('type', None)
        search = request.query_params.get('search', None)
        
        if status_filter:
            shipments = shipments.filter(status=status_filter)
        
        if shipment_type:
            shipments = shipments.filter(shipment_type=shipment_type)
            
        if search:
            shipments = shipments.filter(
                Q(tracking_number__icontains=search) |
                Q(sender_name__icontains=search) |
                Q(receiver_name__icontains=search) |
                Q(receiver_address__icontains=search)
            )
        
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)

class ShipmentTrackView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, tracking_number):
        shipment = get_object_or_404(Shipment, tracking_number=tracking_number)
        shipment_serializer = ShipmentSerializer(shipment)
        
        trackings = shipment.trackings.order_by('timestamp')
        history_serializer = TrackingHistorySerializer(trackings, many=True)
        
        return Response({
            'shipment': shipment_serializer.data,
            'history': history_serializer.data
        })
