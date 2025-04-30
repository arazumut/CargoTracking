from django.urls import path
from .views import ShipmentCreateView, ShipmentListView, ShipmentTrackView

urlpatterns = [
    path('create/', ShipmentCreateView.as_view(), name='shipment-create'),
    path('list/', ShipmentListView.as_view(), name='shipment-list'),
    path('track/<str:tracking_number>/', ShipmentTrackView.as_view(), name='shipment-track'),
]
