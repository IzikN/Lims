from django import forms
from .models import TestRequest, ANALYSIS_CHOICES

class TestRequestForm(forms.ModelForm):
    analysis_types = forms.MultipleChoiceField(
        choices=ANALYSIS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Select Analysis Types"
    )

    class Meta:
        model = TestRequest
        exclude = ['submission_date', 'status']
