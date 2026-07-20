from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import CandidateProfile, RecruiterProfile

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    """
    Form to handle user signup and dynamic profile creation.
    Captures Full Name, Email, Role, and Password.
    """
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'John Doe'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'name@example.com'})
    )
    role = forms.ChoiceField(
        choices=[('candidate', 'Candidate (Job Seeker)'), ('recruiter', 'Recruiter (Employer)')],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select px-3 py-2'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'Min. 8 characters'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'Confirm your password'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['email', 'full_name', 'role', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        if password and len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
            
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # 1. Map role selections
        role = self.cleaned_data.get('role')
        if role == 'candidate':
            user.is_candidate = True
        elif role == 'recruiter':
            user.is_recruiter = True
            
        # 2. Extract first/last name from full_name
        full_name = self.cleaned_data.get('full_name')
        names = full_name.strip().split(' ', 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
            
        # 3. Generate unique username from email
        email = self.cleaned_data.get('email')
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        
        # 4. Set secure password hash
        user.set_password(self.cleaned_data.get('password'))

        if commit:
            user.save()
            # 5. Automatically create corresponding user profiles on database save
            if user.is_candidate:
                CandidateProfile.objects.get_or_create(user=user)
            elif user.is_recruiter:
                RecruiterProfile.objects.get_or_create(user=user)
                
        return user

class UserLoginForm(AuthenticationForm):
    """
    Form to handle custom email-based sign-in.
    """
    username = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'name@example.com'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': '••••••••'})
    )

class UserProfileForm(forms.ModelForm):
    """
    Form to edit core user account settings, primarily Full Name.
    """
    full_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control px-3 py-2', 'placeholder': 'e.g. John Doe'})
    )

    class Meta:
        model = User
        fields = ['full_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['full_name'].initial = self.instance.get_full_name() or self.instance.username

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name')
        names = full_name.strip().split(' ', 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
        else:
            user.last_name = ""
        if commit:
            user.save()
        return user

class CandidateProfileForm(forms.ModelForm):
    """
    Form for Candidates to customize their personal profile information.
    """
    class Meta:
        model = CandidateProfile
        fields = ['phone_number', 'location', 'bio', 'skills', 'profile_picture', 'resume']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. +1 (555) 019-2834'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. San Francisco, CA'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control px-3 py-2',
                'rows': 4,
                'placeholder': 'Tell recruiters about yourself, your background, and your aspirations...'
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. Python, Django, React, Postgres'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control px-3 py-2',
                'accept': 'image/*',
            }),
            'resume': forms.FileInput(attrs={
                'class': 'form-control px-3 py-2',
                'accept': '.pdf,.doc,.docx',
            }),
        }

class RecruiterProfileForm(forms.ModelForm):
    """
    Form for Recruiters to customize their professional profile information.
    """
    class Meta:
        model = RecruiterProfile
        fields = ['phone_number', 'position', 'company_name', 'bio', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. +1 (555) 019-2834'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. Senior Tech Recruiter'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control px-3 py-2',
                'placeholder': 'e.g. Stripe Inc.'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control px-3 py-2',
                'rows': 4,
                'placeholder': 'Tell candidates about your professional focus and organization...'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control px-3 py-2',
                'accept': 'image/*',
            }),
        }
