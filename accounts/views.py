from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
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
    
    if user.is_candidate:
        profile = getattr(user, 'candidate_profile', None)
        my_applications = JobApplication.objects.filter(applicant=user).select_related('job__company')
    elif user.is_recruiter:
        profile = getattr(user, 'recruiter_profile', None)
        my_companies = Company.objects.filter(owner=user)
        my_jobs = Job.objects.filter(company__in=my_companies).select_related('company')
        received_applications = JobApplication.objects.filter(job__company__owner=user).select_related('job', 'applicant')
        
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'my_companies': my_companies,
        'my_jobs': my_jobs,
        'my_applications': my_applications,
        'received_applications': received_applications,
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
