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
    return render(request, 'index.html')

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
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    shipments = Shipment.objects.all()
    if search:
        shipments = shipments.filter(
            Q(tracking_number__icontains=search) |
            Q(sender_name__icontains=search) |
            Q(receiver_name__icontains=search) |
            Q(receiver_address__icontains=search)
        )
    if status:
        shipments = shipments.filter(status=status)
    shipments = shipments.select_related('vehicle', 'driver')
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
        shipment.status = status
        shipment.vehicle = Vehicle.objects.get(id=vehicle_id) if vehicle_id else None
        shipment.driver = Driver.objects.get(id=driver_id) if driver_id else None
        shipment.save()
        Tracking.objects.create(shipment=shipment, status=status)
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
    weekly_count = Shipment.objects.filter(created_at__date__gte=week_ago).count()
    top_cities = Shipment.objects.values('receiver_address').annotate(count=Count('id')).order_by('-count')[:5]
    total = Shipment.objects.count()
    not_delivered = Shipment.objects.exclude(status='delivered').count()
    not_delivered_ratio = (not_delivered / total) * 100 if total > 0 else 0
    active_vehicles = Vehicle.objects.filter(shipments__status__in=['on_the_way', 'in_distribution']).distinct().count()
    total_vehicles = Vehicle.objects.count()
    return render(request, 'reports.html', {
        'weekly_count': weekly_count,
        'top_cities': top_cities,
        'not_delivered_ratio': not_delivered_ratio,
        'active_vehicles': active_vehicles,
        'total_vehicles': total_vehicles
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
