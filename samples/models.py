from django.db import models
from django.conf import settings

class Sample(models.Model):
    SAMPLE_TYPES = [
        ('food', 'Food'),
        ('feed', 'Feed'),
        ('water', 'Water'),
        ('ingredient', 'Raw Material'),
        ('other', 'Other'),
    ]

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'client'})
    sample_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    sample_type = models.CharField(max_length=20, choices=SAMPLE_TYPES)
    description = models.TextField(blank=True)
    date_received = models.DateField()
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_samples', on_delete=models.SET_NULL, null=True, blank=True)
    is_urgent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='Pending')  # e.g., Pending, In Progress, Completed

    def __str__(self):
        return f"{self.sample_id} - {self.name}"

class TestRequest(models.Model):
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE)
    tests_required = models.TextField(help_text="Comma-separated test names")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date_requested = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Request for {self.sample.sample_id}"

class Attachment(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.label or 'Attachment'} for {self.sample.sample_id}"
