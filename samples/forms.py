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
    analyst = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Analyst'),
        label="Assign to Analyst"
    )
    sample = forms.ModelMultipleChoiceField(
        queryset=Sample.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Samples"
    )

    class Meta:
        model = TestAssignment
        fields = ['sample', 'analyst', 'test_parameter', 'sub_parameter', 'deadline']

    def __init__(self, *args, **kwargs):
        client_id = kwargs.pop('client_id', None)
        super().__init__(*args, **kwargs)
        if client_id:
            self.fields['sample'].queryset = Sample.objects.filter(client__client_id=client_id)
        else:
            self.fields['sample'].queryset = Sample.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        test_param = cleaned_data.get('test_parameter')
        sub_param = cleaned_data.get('sub_parameter')
        # Require sub_parameter only if test_parameter is proximate
        if test_param == 'proximate' and not sub_param:
            self.add_error('sub_parameter', 'Please select a sub-parameter')
        if test_param != 'proximate':
            cleaned_data['sub_parameter'] = None
        return cleaned_data


class TestRequestForm(forms.ModelForm):
    analysis_types = forms.MultipleChoiceField(
        choices=ANALYSIS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Select Analysis Types"
    )

    class Meta:
        model = TestRequest
        exclude = ['submitted_by', 'status', 'created_at']
