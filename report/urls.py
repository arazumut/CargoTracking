from django.urls import path
from .views import WeeklyShipmentReportView, TopCitiesReportView, NotDeliveredRatioView, ActiveVehiclesReportView

urlpatterns = [
    path('weekly-shipments/', WeeklyShipmentReportView.as_view(), name='weekly-shipments'),
    path('top-cities/', TopCitiesReportView.as_view(), name='top-cities'),
    path('not-delivered-ratio/', NotDeliveredRatioView.as_view(), name='not-delivered-ratio'),
    path('active-vehicles/', ActiveVehiclesReportView.as_view(), name='active-vehicles'),
]
