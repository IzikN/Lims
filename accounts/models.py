from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('analyst', 'Analyst'),
        ('lab_manager', 'Lab Manager'),
        ('customer_service', 'Customer Service'),
    )
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    staff_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username
