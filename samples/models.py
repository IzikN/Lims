from django.db import models
from django.conf import settings
from django.db import models
from django.conf import settings


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
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.client.name} ({self.client.client_id})"


class Sample(models.Model):
    test_request = models.ForeignKey(TestRequest, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='samples')
    sample_id = models.CharField(max_length=100)
    nature = models.CharField(max_length=255, default='Feed')
    weight = models.DecimalField(max_digits=10, decimal_places=3, default=0)
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
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='assignments')
    analyst = models.ForeignKey(AnalystProfile, on_delete=models.CASCADE)
    test_parameter = models.CharField(max_length=30, choices=TEST_PARAMETERS)
    sub_parameter = models.CharField(max_length=30, blank=True, null=True)
    deadline = models.DateField()
    result = models.TextField(blank=True, null=True)

    def __str__(self):
        if self.test_parameter == 'proximate':
            return f"{self.sample.sample_id} - {self.sub_parameter} assigned"
        return f"{self.sample.sample_id} - {self.test_parameter} assigned"
