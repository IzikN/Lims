from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('lab_manager', 'Lab Manager'),
        ('analyst', 'Analyst'),
        ('qa_officer', 'QA Officer'),
        ('customer_service', 'Customer Service'),
        ('client', 'Client'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company_name = models.CharField(max_length=255, blank=True, null=True)  # for clients


    def __str__(self):
        if self.role == 'client' and self.company_name:
            return f"{self.username} ({self.company_name})"
        return f"{self.username} ({self.get_role_display()})"
