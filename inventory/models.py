from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

class Reagent(models.Model):
    UNIT_CHOICES = [
        ('mL', 'Milliliter'),
        ('L', 'Liter'),
        ('g', 'Gram'),
        ('kg', 'Kilogram'),
        ('mg', 'Milligram'),
        ('each', 'Each'),
    ]
    
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)  # Added
    catalog_number = models.CharField(max_length=50, blank=True)  # Added
    lot_number = models.CharField(max_length=50)
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)  # Added choices
    date_received = models.DateField()
    expiry_date = models.DateField()
    storage_conditions = models.CharField(max_length=100, blank=True)  # Renamed for clarity
    storage_location = models.CharField(max_length=100)
    safety_data_sheet = models.FileField(upload_to='sds/', blank=True, null=True)  # Added
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)  # Added

    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def days_to_expiry(self):
        return (self.expiry_date - timezone.now().date()).days

    @property
    def status(self):
        if self.is_expired():
            return 'Expired'
        elif self.days_to_expiry() <= 30:
            return 'Expiring Soon'
        return 'Good'

    def __str__(self):
        return f"{self.name} (Lot: {self.lot_number})"

    class Meta:
        ordering = ['expiry_date']
        verbose_name = 'Reagent'
        verbose_name_plural = 'Reagents'


class Equipment(models.Model):
    STATUS_CHOICES = [
        ('working', 'Working'),
        ('maintenance', 'Under Maintenance'),
        ('broken', 'Out of Service'),
    ]
    
    name = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100, blank=True)  # Added
    model_number = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100)
    last_calibration_date = models.DateField()
    next_calibration_due = models.DateField()
    calibration_interval = models.PositiveIntegerField(help_text="Interval in days", default=365)  # Added
    calibrated_by = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')  # Enhanced
    maintenance_notes = models.TextField(blank=True)  # Added
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(auto_now=True)  # Added

    def is_due_for_calibration(self):
        return self.next_calibration_due <= timezone.now().date()

    def days_to_calibration(self):
        return (self.next_calibration_due - timezone.now().date()).days

    @property
    def calibration_status(self):
        if self.is_due_for_calibration():
            return 'Due'
        elif self.days_to_calibration() <= 30:
            return 'Due Soon'
        return 'Calibrated'

    def __str__(self):
        return f"{self.name} - {self.serial_number}"

    class Meta:
        ordering = ['next_calibration_due']
        verbose_name = 'Equipment'
        verbose_name_plural = 'Equipment'