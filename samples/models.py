from django.db import models
from django.conf import settings
from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone

class AnalystProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name


class Client(models.Model):
    name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    client_id = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.client_id:
            last = Client.objects.order_by('id').last()
            next_num = last.id + 1 if last else 1
            self.client_id = f"JGLSP{2500 + next_num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.client_id})"


ANALYSIS_CHOICES = [
    ('proximate', 'Proximate'),
    ('aflatoxin', 'Aflatoxin'),
    ('gross_energy', 'Gross Energy'),
    ('metabolizable_energy', 'Metabolizable Energy'),
    ('vitamins', 'Vitamins'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
    ('reviewed', 'Reviewed'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]


class TestRequest(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    organization = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    number_of_samples = models.IntegerField(default=1)
    nature_of_samples = models.TextField(blank=True, default='')
    parameters = models.TextField(default='Proximate', blank=True)
    proposed_date_of_collection = models.DateField(null=True, blank=True)
    total_amount_charged = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    name_of_receiver = models.CharField(max_length=255, default='Unknown')
    job_description = models.CharField(max_length=255, default='N/A', blank=True)
    signature = models.CharField(max_length=255, default='N/A', blank=True)
    analysis_types = models.CharField(max_length=255, choices=ANALYSIS_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True
)
    def __str__(self):
        return f"Request by {self.client.name} ({self.client.client_id})"

class Sample(models.Model):
    TEST_TYPE_CHOICES = [
        ('PROX', 'Proximate'),
        ('AFLX', 'Aflatoxin'),
        ('GREN', 'Gross Energy'),
        ('VIT', 'Vitamins'),
        ('WAT', 'Water'),
        ('MIC', 'Microbial'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    test_type = models.CharField(max_length=4, choices=TEST_TYPE_CHOICES, default='PROX')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    test_request = models.ForeignKey(TestRequest, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='samples')
    sample_id = models.CharField(max_length=100)
    nature = models.CharField(max_length=255, default='Feed')
    weight = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    parameters = models.TextField(default='Proximate')

    def __str__(self):
        return f"{self.sample_id} - {self.nature}"


TEST_PARAMETERS = [
    ('proximate', 'Proximate'),
    ('gross_energy', 'Gross Energy'),
    ('aflatoxin', 'Aflatoxin'),
    ('vitamins', 'Vitamins'),
    ('water_analysis', 'Water Analysis'),
    ('microbial_analysis', 'Microbial Analysis'),
]

PROXIMATE_SUBPARAMETERS = [
    ('ash', 'Ash'),
    ('fiber', 'Fiber'),
    ('moisture', 'Moisture'),
    ('protein', 'Protein'),
    ('fat', 'Fat'),
]

class TestAssignment(models.Model):
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
    ]

    samples = models.ManyToManyField('Sample')
    analyst = models.ForeignKey('AnalystProfile', on_delete=models.CASCADE)
    test_parameter = models.CharField(max_length=30, choices=TEST_PARAMETERS)
    sub_parameter = models.CharField(max_length=30, blank=True, null=True)
    deadline = models.DateField()
    result = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    started = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    review_comments = models.TextField(blank=True, null=True)
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_test_requests'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_test_requests'
    )
    review_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )

    def __str__(self):
        sample_ids = ', '.join(s.sample_id for s in self.samples.all())
        if self.test_parameter == 'proximate':
            return f"{sample_ids} - {self.sub_parameter} assigned"
        return f"{sample_ids} - {self.test_parameter} assigned"



class ReviewLog(models.Model):
    assignment = models.ForeignKey('TestAssignment', on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    comments = models.TextField(blank=True, null=True)
    decision = models.CharField(max_length=10, choices=[('approved', 'Approved'), ('rejected', 'Rejected')])
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer} - {self.decision} on {self.reviewed_at.strftime('%Y-%m-%d %H:%M')}"

from django.utils.crypto import get_random_string

class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    test_request = models.OneToOneField(TestRequest, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_generated = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid')

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = 'JGL' + get_random_string(8).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"

class ResultReport(models.Model):
    client_id = models.CharField(max_length=50)
    sample = models.ForeignKey('Sample', on_delete=models.CASCADE)
    test_parameter = models.CharField(max_length=100)
    result_value = models.CharField(max_length=100)
    method_reference = models.CharField(max_length=255, default='AOAC')
    approved = models.BooleanField(default=False)
    report_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.client_id} - {self.sample.sample_id} - {self.test_parameter}"
