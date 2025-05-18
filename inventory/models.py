from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class EquipmentLog(models.Model):
    EQUIPMENT_CHOICES = [
        ('fibertec', 'Fibertec'),
        ('kjeltec_8200', 'Kjeltec 8200'),
        ('kjeltec_8400', 'Kjeltec 8400'),
        ('moisture_analyzer', 'Moisture Analyzer'),
        ('furnace', 'Furnace'),
        ('oven', 'Oven'),
        ('centrifuge', 'Centrifuge'),
        ('digestor', 'Digestor'),
    ]

    STATUS_CHOICES = [
        ('working', 'Working'),
        ('maintenance', 'Maintenance'),
        ('broken', 'Broken'),
        ('idle', 'Idle'),
    ]

    equipment_name = models.CharField(max_length=50, choices=EQUIPMENT_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, editable=False)
    analyst = models.CharField(max_length=50, choices=[('analyst_a', 'Analyst A'), ('analyst_b', 'Analyst B'), ('analyst_c', 'Analyst C')])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    signed_by = models.CharField(max_length=100)
    reviewed_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate hours_worked automatically (in decimal hours)
        delta = self.end_time - self.start_time
        self.hours_worked = round(delta.total_seconds() / 3600, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_equipment_name_display()} - {self.analyst} on {self.start_time.strftime('%Y-%m-%d')}"


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
    date_added = models.DateTimeField(default=timezone.now)

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
    date_added = models.DateTimeField(default=timezone.now)

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