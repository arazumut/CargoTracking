from django.urls import path
from .views import AssignVehicleDriverView

urlpatterns = [
    path('assign/<int:shipment_id>/', AssignVehicleDriverView.as_view(), name='assign-vehicle-driver'),
]
