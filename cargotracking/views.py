from datetime import timedelta, date
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from user.models import UserProfile
from shipment.models import Shipment
from tracking.models import Tracking
from vehicle.models import Vehicle, Driver
from django.contrib.auth.models import User

def index(request):
    # Kullanıcı giriş yapmışsa ve profili varsa rol bilgisini al
    role = None
    if request.user.is_authenticated:
        user_profile = getattr(request.user, 'profile', None)
        if user_profile:
            role = user_profile.role
    
    # Son 5 kargo durumunu getir (herkes için görünür)
    recent_shipments = []
    if request.user.is_authenticated:
        if role in ['operator', 'admin']:
            # Operatör ve admin için tüm kargolar
            recent_shipments = Shipment.objects.all().order_by('-created_at')[:5]
        else:
            # Normal müşteri - şimdilik boş bırakıyoruz
            # Gerçek uygulamada müşterinin kendi kargoları gösterilebilir
            pass
    
    return render(request, 'index.html', {
        'user_role': role,
        'recent_shipments': recent_shipments
    })

def tracking_result(request):
    tracking_number = request.GET.get('tracking_number')
    shipment = None
    history = []
    if tracking_number:
        shipment = Shipment.objects.filter(tracking_number=tracking_number).first()
        if shipment:
            history = shipment.trackings.order_by('timestamp')
    return render(request, 'tracking_result.html', {
        'shipment': shipment,
        'history': history,
        'tracking_number': tracking_number
    })

def shipment_create(request):
    tracking_number = None
    if request.method == 'POST':
        data = request.POST
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
        tracking_number = shipment.tracking_number
    return render(request, 'shipment_create.html', {'tracking_number': tracking_number})

@login_required
def operation_panel(request):
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or user_profile.role not in ['operator', 'admin']:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('index')
    
    # Filtreler için parametreleri al
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    date_range = request.GET.get('date_range', '')
    shipment_type = request.GET.get('shipment_type', '')
    
    # Temel sorgu
    shipments = Shipment.objects.all()
    
    # Metin araması
    if search:
        shipments = shipments.filter(
            Q(tracking_number__icontains=search) |
            Q(sender_name__icontains=search) |
            Q(receiver_name__icontains=search) |
            Q(receiver_address__icontains=search)
        )
    
    # Durum filtresi
    if status:
        shipments = shipments.filter(status=status)
    
    # Gönderi türü filtresi
    if shipment_type:
        shipments = shipments.filter(shipment_type=shipment_type)
    
    # Tarih aralığı filtresi
    today = date.today()
    if date_range == 'today':
        shipments = shipments.filter(created_at__date=today)
    elif date_range == 'yesterday':
        yesterday = today - timedelta(days=1)
        shipments = shipments.filter(created_at__date=yesterday)
    elif date_range == 'last_week':
        week_ago = today - timedelta(days=7)
        shipments = shipments.filter(created_at__date__gte=week_ago)
    elif date_range == 'last_month':
        month_ago = today - timedelta(days=30)
        shipments = shipments.filter(created_at__date__gte=month_ago)
    
    # İlişkili veri önceden yükle (N+1 sorgusunu önlemek için)
    shipments = shipments.select_related('vehicle', 'driver')
    
    # Sıralama
    shipments = shipments.order_by('-created_at')
    
    return render(request, 'operation_panel.html', {'shipments': shipments})

@login_required
def operation_update(request, shipment_id):
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or user_profile.role not in ['operator', 'admin']:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('index')
    
    shipment = get_object_or_404(Shipment, id=shipment_id)
    vehicles = Vehicle.objects.all()
    drivers = Driver.objects.all()
    
    if request.method == 'POST':
        status = request.POST.get('status')
        vehicle_id = request.POST.get('vehicle')
        driver_id = request.POST.get('driver')
        note = request.POST.get('note', '')
        
        # Durum değişikliği var mı kontrol edelim
        status_changed = shipment.status != status
        
        shipment.status = status
        shipment.vehicle = Vehicle.objects.get(id=vehicle_id) if vehicle_id else None
        shipment.driver = Driver.objects.get(id=driver_id) if driver_id else None
        shipment.save()
        
        # Durum değiştiğinde veya not eklendiğinde yeni takip kaydı oluşturalım
        if status_changed or note:
            Tracking.objects.create(
                shipment=shipment,
                status=status,
                note=note
            )
        
        messages.success(request, 'Kargo bilgileri başarıyla güncellendi.')
        return redirect('operation-panel')
    
    return render(request, 'operation_update.html', {
        'shipment': shipment,
        'vehicles': vehicles,
        'drivers': drivers
    })

@login_required
def reports(request):
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or user_profile.role not in ['operator', 'admin']:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('index')
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Haftalık gönderi sayısı
    weekly_count = Shipment.objects.filter(created_at__date__gte=week_ago).count()
    
    # En çok gönderilen şehirler
    top_cities = Shipment.objects.values('receiver_address').annotate(count=Count('id')).order_by('-count')[:5]
    total_shipments = Shipment.objects.count()
    
    # Her bir şehir için yüzde ekle
    for city in top_cities:
        city['percentage'] = (city['count'] / total_shipments * 100) if total_shipments > 0 else 0
    
    # Teslimat oranları
    total = Shipment.objects.count()
    delivered = Shipment.objects.filter(status='delivered').count()
    not_delivered = Shipment.objects.filter(status='not_delivered').count()
    in_progress = total - (delivered + not_delivered)
    
    not_delivered_ratio = (not_delivered / total * 100) if total > 0 else 0
    delivery_success_rate = (delivered / total * 100) if total > 0 else 0
    
    # Zamanında teslim oranı hesapla (tahmini teslim tarihinden önce teslim edilenler)
    on_time_deliveries = Shipment.objects.filter(
        status='delivered',
        estimated_delivery__gte=date.today()
    ).count()
    
    on_time_ratio = (on_time_deliveries / delivered * 100) if delivered > 0 else 0
    
    # Araç kullanımı
    active_vehicles = Vehicle.objects.filter(shipments__status__in=['on_the_way', 'in_distribution']).distinct().count()
    total_vehicles = Vehicle.objects.count()
    
    # Gönderi türü dağılımı
    shipment_types = Shipment.objects.values('shipment_type').annotate(count=Count('id'))
    shipment_type_data = {item['shipment_type']: item['count'] for item in shipment_types}
    
    # Durum dağılımı
    status_counts = Shipment.objects.values('status').annotate(count=Count('id'))
    status_data = {item['status']: item['count'] for item in status_counts}
    
    # Sürücü performansı (örnek veri - gerçek uygulamada daha karmaşık sorgular gerekebilir)
    driver_performance = []
    drivers = Driver.objects.all()
    for driver in drivers[:5]:  # İlk 5 sürücü
        total_deliveries = Shipment.objects.filter(driver=driver).count()
        successful_deliveries = Shipment.objects.filter(driver=driver, status='delivered').count()
        success_rate = (successful_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
        
        # Bu hesaplama gerçek uygulamada daha karmaşık olabilir
        avg_delivery_time = 1.5  # Örnek değer
        
        driver_performance.append({
            'name': driver.name,
            'total_deliveries': total_deliveries,
            'successful_deliveries': successful_deliveries,
            'success_rate': success_rate,
            'avg_delivery_time': avg_delivery_time
        })
    
    return render(request, 'reports.html', {
        'weekly_count': weekly_count,
        'top_cities': top_cities,
        'not_delivered_ratio': not_delivered_ratio,
        'delivery_success_rate': delivery_success_rate,
        'on_time_ratio': on_time_ratio,
        'active_vehicles': active_vehicles,
        'total_vehicles': total_vehicles,
        'shipment_type_data': shipment_type_data,
        'status_data': status_data,
        'driver_performance': driver_performance,
        'total_shipments': total_shipments,
        'delivered': delivered,
        'not_delivered': not_delivered,
        'in_progress': in_progress
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı!')
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

def user_register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        email = request.POST.get('email')
        role = request.POST.get('role', 'customer')
        
        if password != password_confirm:
            messages.error(request, 'Şifreler eşleşmiyor!')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu kullanıcı adı zaten alınmış!')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Bu e-posta adresi zaten kullanılıyor!')
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            from user.models import UserProfile
            UserProfile.objects.create(user=user, role=role)
            messages.success(request, 'Kayıt başarılı! Giriş yapabilirsiniz.')
            return redirect('login')
    return render(request, 'register.html')
