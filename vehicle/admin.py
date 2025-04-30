from django.contrib import admin
from .models import Vehicle, Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'license_class']
    search_fields = ['name', 'phone']

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate', 'model', 'capacity_kg', 'capacity_m3', 'driver']
    search_fields = ['plate', 'model']
    list_filter = ['driver']
