from django.db import models

class Tracking(models.Model):
    STATUS_CHOICES = [
        ('preparing', 'Hazırlanıyor'),
        ('on_the_way', 'Yolda'),
        ('in_distribution', 'Dağıtımda'),
        ('delivered', 'Teslim Edildi'),
        ('not_delivered', 'Teslim Edilemedi'),
    ]
    shipment = models.ForeignKey('shipment.Shipment', on_delete=models.CASCADE, related_name='trackings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.get_status_display()} @ {self.timestamp}"
