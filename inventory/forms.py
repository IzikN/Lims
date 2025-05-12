from django import forms
from .models import Reagent, Equipment

class ReagentForm(forms.ModelForm):
    class Meta:
        model = Reagent
        fields = '__all__'
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'date_received': forms.DateInput(attrs={'type': 'date'}),
        }

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = '__all__'
        widgets = {
            'last_calibration_date': forms.DateInput(attrs={'type': 'date'}),
            'next_calibration_due': forms.DateInput(attrs={'type': 'date'}),
        }
