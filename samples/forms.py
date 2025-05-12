from django import forms
from django.utils.timezone import now
from .models import Sample

class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['sample_id', 'name', 'sample_type', 'description', 'client_email', 'client_company_address', 'client_company', 'weight', 'analysis_type', 'is_urgent']
    
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'company_address': forms.Textarea(attrs={'rows': 2}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.client_id:
            year_short = now().year % 100  # e.g., 2025 → 25
            count = Sample.objects.filter(client_id__startswith=f"JGLSP{year_short}").count() + 1
            instance.client_id = f"JGLSP{year_short:02d}{count:04d}"
        if commit:
            instance.save()
        return instance
