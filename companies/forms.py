from django import forms
from .models import Company

class CompanyForm(forms.ModelForm):
    """
    Form for recruiters to create and update company profile listings.
    """
    class Meta:
        model = Company
        fields = ['name', 'description', 'website', 'location', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. Stripe Inc.'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control px-3 py-2',
                'rows': 5,
                'placeholder': 'Provide a detailed description of the company culture, mission, and products...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. https://stripe.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. San Francisco, CA'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control px-3 py-2',
                'accept': 'image/*',
            }),
        }

    def clean_name(self):
        """
        Validate name field to ensure uniqueness, ignoring case issues.
        """
        name = self.cleaned_data.get('name')
        # Check uniqueness while editing vs. creating
        queryset = Company.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError("A company with this name is already registered on HireFlow.")
        return name
