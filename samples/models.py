from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Sample(models.Model):
    SAMPLE_TYPES = [
        ('food', 'Food'),
        ('feed', 'Feed'),
        ('water', 'Water'),
        ('ingredient', 'Raw Material'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    sample_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Assuming User model is used for clients
        related_name='samples',  # This is the reverse relationship from User
        on_delete=models.CASCADE,
        null=True,  # Clients may not be present initially
        blank=True
    )
    analysis_type = models.CharField(max_length=100, choices=SAMPLE_TYPES, blank=True, null=True)
    sample_type = models.CharField(max_length=50, choices=SAMPLE_TYPES, null=True, blank=True)
    description = models.TextField(blank=True)
    client_email = models.EmailField(null=True)
    client_company_address = models.CharField(max_length=255, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # e.g., in grams or kg
    is_urgent = models.BooleanField(default=False)

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='received_samples',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sample_id} - {self.name}"



class TestRequest(models.Model):
    TEST_TYPES = [
        ('proximate', 'Proximate Analysis'),
        ('ge', 'Gross Energy'),
        ('vitamin', 'Vitamin Analysis'),
        ('aflatoxin', 'Aflatoxin Testing'),
        ('water', 'Water Analysis'),
        ('microbial', 'Microbial Analysis'),
    ]

    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    tests_required = models.TextField(help_text="Comma-separated test names")
    test_type = models.CharField(max_length=50, choices=TEST_TYPES, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_test_requests'
    )
    date_requested = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Request for {self.sample.sample_id}"


class TestAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('submitted', 'Submitted for Review'),
    ]

    REVIEW_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    test_request = models.ForeignKey(
        TestRequest,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    analyst = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_tests'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_by_user'
    )
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviews_done'
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='pending')

    assigned_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    result_data = models.TextField(blank=True, null=True)
    result_file = models.FileField(upload_to='results/', blank=True, null=True)
    review_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.test_request.get_test_type_display()} for {self.test_request.sample.sample_id}"

    @property
    def sample(self):
        return self.test_request.sample

    class Meta:
        ordering = ['-assigned_at']
        verbose_name = 'Test Assignment'
        verbose_name_plural = 'Test Assignments'


class Attachment(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    label = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.label or 'Attachment'} for {self.sample.sample_id}"
