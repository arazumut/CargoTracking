from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from shipment.models import Shipment
from vehicle.models import Vehicle, Driver
from django.db.models import Count, Q, Avg
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

class DashboardReportView(APIView):
    """Genel bir dashboard için gereken tüm rapor verilerini tek bir API çağrısıyla döndürür."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        today = date.today()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Zaman bazlı istatistikler
        weekly_count = Shipment.objects.filter(created_at__date__gte=week_ago).count()
        monthly_count = Shipment.objects.filter(created_at__date__gte=month_ago).count()
        today_count = Shipment.objects.filter(created_at__date=today).count()
        
        # En çok kullanılan şehirler
        top_cities = Shipment.objects.values('receiver_address').annotate(count=Count('id')).order_by('-count')[:5]
        total_shipments = Shipment.objects.count()
        
        # Her bir şehir için yüzde ekle
        for city in top_cities:
            city['percentage'] = (city['count'] / total_shipments * 100) if total_shipments > 0 else 0
        
        # Teslimat oranları
        delivered = Shipment.objects.filter(status='delivered').count()
        not_delivered = Shipment.objects.filter(status='not_delivered').count()
        in_progress = total_shipments - (delivered + not_delivered)
        
        delivery_success_rate = (delivered / total_shipments * 100) if total_shipments > 0 else 0
        not_delivered_ratio = (not_delivered / total_shipments * 100) if total_shipments > 0 else 0
        
        # Zamanında teslim oranı
        on_time_deliveries = Shipment.objects.filter(
            status='delivered',
            estimated_delivery__gte=date.today()
        ).count()
        
        on_time_ratio = (on_time_deliveries / delivered * 100) if delivered > 0 else 0
        
        # Araç kullanımı
        active_vehicles = Vehicle.objects.filter(shipments__status__in=['on_the_way', 'in_distribution']).distinct().count()
        total_vehicles = Vehicle.objects.count()
        vehicle_usage_rate = (active_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0
        
        # Gönderi türü dağılımı
        shipment_types = Shipment.objects.values('shipment_type').annotate(count=Count('id'))
        shipment_type_data = {item['shipment_type']: item['count'] for item in shipment_types}
        
        # Durum dağılımı
        status_counts = Shipment.objects.values('status').annotate(count=Count('id'))
        status_data = {item['status']: item['count'] for item in status_counts}
        
        # Sürücü performansı
        driver_performance = []
        drivers = Driver.objects.all()
        for driver in drivers[:5]:  # İlk 5 sürücü
            total_driver_deliveries = Shipment.objects.filter(driver=driver).count()
            successful_deliveries = Shipment.objects.filter(driver=driver, status='delivered').count()
            success_rate = (successful_deliveries / total_driver_deliveries * 100) if total_driver_deliveries > 0 else 0
            
            driver_performance.append({
                'id': driver.id,
                'name': driver.name,
                'total_deliveries': total_driver_deliveries,
                'successful_deliveries': successful_deliveries,
                'success_rate': success_rate
            })
            
        return Response({
            'time_stats': {
                'today_count': today_count,
                'weekly_count': weekly_count,
                'monthly_count': monthly_count,
                'total_count': total_shipments
            },
            'delivery_stats': {
                'delivered': delivered,
                'not_delivered': not_delivered,
                'in_progress': in_progress,
                'delivery_success_rate': delivery_success_rate,
                'not_delivered_ratio': not_delivered_ratio,
                'on_time_ratio': on_time_ratio
            },
            'location_stats': {
                'top_cities': top_cities
            },
            'vehicle_stats': {
                'active_vehicles': active_vehicles,
                'total_vehicles': total_vehicles,
                'usage_rate': vehicle_usage_rate 
            },
            'shipment_types': shipment_type_data,
            'status_distribution': status_data,
            'driver_performance': driver_performance
        })
