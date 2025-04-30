from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from shipment.models import Shipment
from vehicle.models import Vehicle
from django.db.models import Count, Q
from datetime import timedelta, date

class WeeklyShipmentReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = date.today()
        week_ago = today - timedelta(days=7)
        count = Shipment.objects.filter(created_at__date__gte=week_ago).count()
        return Response({'weekly_shipment_count': count})

class TopCitiesReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        city_counts = Shipment.objects.values('receiver_address').annotate(count=Count('id')).order_by('-count')[:5]
        return Response({'top_cities': city_counts})

class NotDeliveredRatioView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total = Shipment.objects.count()
        not_delivered = Shipment.objects.filter(~Q(status='delivered')).count()
        ratio = (not_delivered / total) * 100 if total > 0 else 0
        return Response({'not_delivered_ratio': ratio})

class ActiveVehiclesReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        active_vehicles = Vehicle.objects.filter(shipments__status__in=['on_the_way', 'in_distribution']).distinct().count()
        total_vehicles = Vehicle.objects.count()
        return Response({'active_vehicles': active_vehicles, 'total_vehicles': total_vehicles})
