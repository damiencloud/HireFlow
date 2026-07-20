from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, CandidateProfileForm, RecruiterProfileForm
from .models import CandidateProfile, RecruiterProfile
from companies.models import Company
from jobs.models import Job, JobApplication, SavedJob

def register(request):
    """
    Handles candidate/recruiter registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Welcome to HireFlow, {user.first_name}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please check form errors.")
    else:
        form = UserRegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

def _shared_login(request, template_name):
    """
    Reusable login helper for standard, candidate, and recruiter login views.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = UserLoginForm(request)
        
    return render(request, template_name, {'form': form})

def login(request):
    return _shared_login(request, 'accounts/login.html')

def candidate_login(request):
    return _shared_login(request, 'accounts/candidate-login.html')

def recruiter_login(request):
    return _shared_login(request, 'accounts/recruiter-login.html')



@login_required
def dashboard(request):
    """
    Displays role-specific analytics and profile details for authenticated users.
    """
    user = request.user
    profile = None
    my_companies = []
    my_jobs = []
    my_applications = []
    received_applications = []
    completeness = 0
    checklist = []
    
    if user.is_candidate:
        profile, created = CandidateProfile.objects.get_or_create(user=user)
        my_applications = JobApplication.objects.filter(applicant=user).select_related('job__company')
        
        checklist = [
            {'label': 'Account Created', 'done': True},
            {'label': 'Phone Number Added', 'done': bool(profile.phone_number)},
            {'label': 'Location Added', 'done': bool(profile.location)},
            {'label': 'Skills Configured', 'done': bool(profile.skills)},
            {'label': 'Bio Written', 'done': bool(profile.bio)},
            {'label': 'Profile Photo Uploaded', 'done': bool(profile.profile_picture)},
            {'label': 'Resume CV Uploaded', 'done': bool(profile.resume)},
        ]
        done_count = sum(1 for item in checklist if item['done'])
        completeness = int((done_count / len(checklist)) * 100)
        
    elif user.is_recruiter:
        profile, created = RecruiterProfile.objects.get_or_create(user=user)
        my_companies = Company.objects.filter(owner=user)
        my_jobs = Job.objects.filter(company__in=my_companies).select_related('company')
        received_applications = JobApplication.objects.filter(job__company__owner=user).select_related('job', 'applicant')
        
        checklist = [
            {'label': 'Account Created', 'done': True},
            {'label': 'Phone Number Added', 'done': bool(profile.phone_number)},
            {'label': 'Bio Written', 'done': bool(profile.bio)},
            {'label': 'Position Specified', 'done': bool(profile.position)},
            {'label': 'Company Affiliation Added', 'done': bool(profile.company_name)},
            {'label': 'Profile Photo Uploaded', 'done': bool(profile.profile_picture)},
        ]
        done_count = sum(1 for item in checklist if item['done'])
        completeness = int((done_count / len(checklist)) * 100)
        
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'my_companies': my_companies,
        'my_jobs': my_jobs,
        'my_applications': my_applications,
        'received_applications': received_applications,
        'completeness': completeness,
        'checklist': checklist,
    })

def logout_view(request):
    """
    Logs out the user and redirects to the index landing page.
    """
    auth_logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('index')

@login_required
def saved_jobs(request):
    """
    Renders candidate saved jobs list.
    """
    if not request.user.is_candidate:
        messages.error(request, "Only candidates are authorized to view saved jobs.")
        return redirect('dashboard')
        
    bookmarks = SavedJob.objects.filter(user=request.user).select_related('job__company')
    return render(request, 'accounts/saved-jobs.html', {
        'saved_jobs': bookmarks
    })

@login_required
def edit_profile(request):
    """
    Renders and processes profile customizer edits. Handles both Candidate and Recruiter fields.
    """
    user = request.user
    profile = None
    
    if user.is_candidate:
        profile, created = CandidateProfile.objects.get_or_create(user=user)
        ProfileFormClass = CandidateProfileForm
    elif user.is_recruiter:
        profile, created = RecruiterProfile.objects.get_or_create(user=user)
        ProfileFormClass = RecruiterProfileForm
    else:
        messages.error(request, "Your account role does not support profile editing.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=user)
        profile_form = ProfileFormClass(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        user_form = UserProfileForm(instance=user)
        profile_form = ProfileFormClass(instance=profile)
        
    return render(request, 'accounts/edit-profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })
