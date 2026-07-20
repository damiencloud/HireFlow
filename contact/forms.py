from django import forms
from .models import ContactMessage

class ContactForm(forms.ModelForm):
    """
    Form to capture user support and contact submissions.
    """
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'John Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'johndoe@example.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'How can we help you?'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control px-3 py-2',
                'rows': 5,
                'placeholder': 'Write your message here...',
                'style': 'resize: none;'
            }),
        }
