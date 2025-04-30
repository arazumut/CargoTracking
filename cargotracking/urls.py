"""
URL configuration for cargotracking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import index, tracking_result, shipment_create, operation_panel, operation_update, reports, user_login, user_logout, user_register

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('api/shipment/', include('shipment.urls')),
    path('api/tracking/', include('tracking.urls')),
    path('api/vehicle/', include('vehicle.urls')),
    path('api/user/', include('user.urls')),
    path('api/report/', include('report.urls')),
    path('tracking-result/', tracking_result, name='tracking-result'),
    path('shipment-create/', shipment_create, name='shipment-create'),
    path('operation-panel/', operation_panel, name='operation-panel'),
    path('operation-panel/update/<int:shipment_id>/', operation_update, name='operation-update'),
    path('reports/', reports, name='reports'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', user_register, name='register'),
]
