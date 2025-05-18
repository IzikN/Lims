from django import forms
from .models import Reagent, Equipment
from .models import EquipmentLog

class EquipmentLogForm(forms.ModelForm):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = EquipmentLog
        fields = ['equipment_name', 'start_time', 'end_time', 'analyst', 'status', 'signed_by', 'reviewed_by']


class EquipmentFilterForm(forms.Form):
    name = forms.CharField(required=False, label="Equipment Name")
    category = forms.CharField(required=False)

class ReagentFilterForm(forms.Form):
    name = forms.CharField(required=False, label="Reagent Name")
    supplier = forms.CharField(required=False)


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
