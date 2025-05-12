from django import forms
from django.utils.timezone import now
from .models import Sample

class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['sample_id', 'name', 'client', 'analysis_type', 'sample_type', 
                  'description', 'client_email', 'client_company_address', 
                  'weight', 'is_urgent', 'received_by', 'status']
        widgets = {
            'client': forms.Select(),  # This will render a dropdown for the client (User model)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally, you can filter the 'client' field to only show 'clients' in the dropdown
        self.fields['client'].queryset = self.fields['client'].queryset.filter(role='client')


    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.client_id:
            year_short = now().year % 100  # e.g., 2025 → 25
            count = Sample.objects.filter(client_id__startswith=f"JGLSP{year_short}").count() + 1
            instance.client_id = f"JGLSP{year_short:02d}{count:04d}"
        if commit:
            instance.save()
        return instance
