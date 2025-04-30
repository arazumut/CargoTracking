from django.db import models
from django.utils.crypto import get_random_string
from django.utils import timezone

class Shipment(models.Model):
    SHIPMENT_TYPE_CHOICES = [
        ('document', 'Belge'),
        ('box', 'Koli'),
        ('pallet', 'Palet'),
        ('other', 'Diğer'),
    ]
    STATUS_CHOICES = [
        ('preparing', 'Hazırlanıyor'),
        ('on_the_way', 'Yolda'),
        ('in_distribution', 'Dağıtımda'),
        ('delivered', 'Teslim Edildi'),
        ('not_delivered', 'Teslim Edilemedi'),
    ]
    sender_name = models.CharField(max_length=100)
    sender_address = models.CharField(max_length=255)
    sender_phone = models.CharField(max_length=20)
    receiver_name = models.CharField(max_length=100)
    receiver_address = models.CharField(max_length=255)
    receiver_phone = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    estimated_delivery = models.DateField()
    tracking_number = models.CharField(max_length=12, unique=True, editable=False)
    shipment_type = models.CharField(max_length=20, choices=SHIPMENT_TYPE_CHOICES)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    volume_m3 = models.DecimalField(max_digits=6, decimal_places=3)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparing')
    created_at = models.DateTimeField(auto_now_add=True)
    vehicle = models.ForeignKey('vehicle.Vehicle', on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    driver = models.ForeignKey('vehicle.Driver', on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = self.generate_tracking_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_tracking_number():
        return get_random_string(length=12, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ23456789')

    def __str__(self):
        return f"{self.tracking_number} - {self.sender_name} -> {self.receiver_name}"
