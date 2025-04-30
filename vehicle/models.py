from django.db import models

# Create your models here.
class Driver(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    license_class = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.license_class})"

class Vehicle(models.Model):
    model = models.CharField(max_length=100)
    plate = models.CharField(max_length=20, unique=True)
    capacity_kg = models.DecimalField(max_digits=7, decimal_places=2)
    capacity_m3 = models.DecimalField(max_digits=7, decimal_places=3)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles')

    def __str__(self):
        return f"{self.plate} - {self.model}"
