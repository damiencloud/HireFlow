from django import forms
from .models import Job
from companies.models import Company

class JobPostingForm(forms.ModelForm):
    """
    Form for recruiters to create new job vacancy listings.
    """
    class Meta:
        model = Job
        fields = [
            'company', 'title', 'description', 'category', 
            'location', 'salary', 'job_type', 'experience_level', 'deadline'
        ]
        widgets = {
            'company': forms.Select(attrs={'class': 'form-select px-3 py-2'}),
            'title': forms.TextInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'e.g. Senior React Developer'}),
            'description': forms.Textarea(attrs={'class': 'form-control px-3 py-2', 'rows': 5, 'placeholder': 'Describe the role, responsibilities, and requirements...'}),
            'category': forms.Select(attrs={'class': 'form-select px-3 py-2'}),
            'location': forms.TextInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'e.g. San Francisco, CA or Remote'}),
            'salary': forms.TextInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'e.g. $120,000 - $140,000 /yr'}),
            'job_type': forms.Select(attrs={'class': 'form-select px-3 py-2'}),
            'experience_level': forms.Select(attrs={'class': 'form-select px-3 py-2'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control px-3 py-2', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            # Dynamically restrict company options to those owned by the current recruiter
            self.fields['company'].queryset = Company.objects.filter(owner=user)
