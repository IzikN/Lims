from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class ClientRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'company_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'style': 'height: 45px;',
                'placeholder': field.label
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'client'
        if commit:
            user.save()
        return user


class StaffRegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('analyst', 'Analyst'),
        ('lab_manager', 'Lab Manager'),
        ('customer_service', 'Customer Service'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'staff_name', 'role', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'style': 'height: 45px;',
                'placeholder': field.label
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user
