from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Vehicle, Driver
from shipment.models import Shipment
from django.shortcuts import get_object_or_404
from django.db.models import Sum

class AssignVehicleDriverView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, shipment_id):
        shipment = get_object_or_404(Shipment, id=shipment_id)
        vehicle_id = request.data.get('vehicle_id')
        driver_id = request.data.get('driver_id')
        vehicle = get_object_or_404(Vehicle, id=vehicle_id)
        driver = get_object_or_404(Driver, id=driver_id)
        # Kapasite kontrolü
        total_weight = Shipment.objects.filter(vehicle=vehicle).aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
        total_volume = Shipment.objects.filter(vehicle=vehicle).aggregate(Sum('volume_m3'))['volume_m3__sum'] or 0
        if total_weight + shipment.weight_kg > vehicle.capacity_kg or total_volume + shipment.volume_m3 > vehicle.capacity_m3:
            return Response({'error': 'Araç kapasitesi aşıldı!'}, status=status.HTTP_400_BAD_REQUEST)
        shipment.vehicle = vehicle
        shipment.driver = driver
        shipment.save()
        return Response({'message': 'Araç ve şoför atandı.'})
