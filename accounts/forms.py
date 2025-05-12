# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'company_name', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        company_name = cleaned_data.get("company_name")

        if role == "client" and not company_name:
            self.add_error('company_name', "Clients must enter a company name.")
        elif role != "client":
            cleaned_data['company_name'] = None

        return cleaned_data
