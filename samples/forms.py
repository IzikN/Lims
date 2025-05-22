from django import forms
from .models import TestRequest, ANALYSIS_CHOICES, TestAssignment, Sample, TEST_PARAMETERS, PROXIMATE_SUBPARAMETERS
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class SubmitResultForm(forms.ModelForm):
    class Meta:
        model = TestAssignment
        fields = ['result']
        widgets = {
            'result': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
        }


class TestAssignmentForm(forms.ModelForm):
    class Meta:
        model = TestAssignment
        fields = ['analyst', 'test_parameter', 'sub_parameter', 'deadline', 'samples']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically load analysts
        self.fields['analyst'].queryset = AnalystProfile.objects.all()
        self.fields['analyst'].label_from_instance = lambda obj: f"{obj.full_name}"

class TestRequestForm(forms.ModelForm):
    analysis_types = forms.MultipleChoiceField(
        choices=ANALYSIS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Select Analysis Types"
    )

    class Meta:
        model = TestRequest
        exclude = ['submitted_by', 'status', 'created_at']
