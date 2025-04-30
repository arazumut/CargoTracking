from django.urls import path
from .views import TrackingHistoryView, TrackingStatusUpdateView

urlpatterns = [
    path('history/<int:shipment_id>/', TrackingHistoryView.as_view(), name='tracking-history'),
    path('update-status/<int:shipment_id>/', TrackingStatusUpdateView.as_view(), name='tracking-status-update'),
]
