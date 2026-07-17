from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job, JobApplication
from .forms import JobPostingForm, JobApplicationForm
from companies.models import Company

def jobs(request):
    """
    Renders the main job board list with support for search and multi-parameter filtering.
    """
    queryset = Job.objects.select_related('company').all()

    # 1. Keyword search (looks at job title, job description, or company name)
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(company__name__icontains=q)
        )

    # 2. Location filtering
    location = request.GET.get('location', '').strip()
    if location:
        queryset = queryset.filter(location__icontains=location)

    # 3. Category filtering
    category = request.GET.get('category', '').strip()
    if category and category != 'all':
        queryset = queryset.filter(category=category)

    # 4. Job type filtering (Full-time, remote, etc)
    job_type = request.GET.get('job_type', '').strip()
    if job_type and job_type != 'all':
        queryset = queryset.filter(job_type=job_type)

    # 5. Experience level filtering
    experience_level = request.GET.get('experience_level', '').strip()
    if experience_level and experience_level != 'all':
        queryset = queryset.filter(experience_level=experience_level)

    # Get available list classifications to populate dropdown structures in the frontend
    categories = Job.CATEGORY_CHOICES
    job_types = Job.JOB_TYPE_CHOICES
    experience_levels = Job.EXPERIENCE_CHOICES

    return render(request, 'jobs/jobs.html', {
        'jobs': queryset,
        'q': q,
        'location': location,
        'category_filter': category,
        'job_type_filter': job_type,
        'experience_filter': experience_level,
        'categories': categories,
        'job_types': job_types,
        'experience_levels': experience_levels,
    })

def job_details(request, job_id=None):
    """
    Displays the details of a single job. Passes application forms for active candidate sessions.
    """
    if job_id is None:
        job = Job.objects.first()
        if not job:
            messages.info(request, "No job vacancies listed yet.")
            return redirect('index')
    else:
        job = get_object_or_404(Job, pk=job_id)
        
    apply_form = None
    already_applied = False
    if request.user.is_authenticated and request.user.is_candidate:
        apply_form = JobApplicationForm()
        already_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
        
    return render(request, 'jobs/job-details.html', {
        'job': job,
        'apply_form': apply_form,
        'already_applied': already_applied,
    })

@login_required
def job_posting(request):
    """
    Recruiter-only view to publish new job listings.
    """
    # Restrict view access to recruiter users only
    if not request.user.is_recruiter:
        messages.error(request, "Only recruiters are authorized to publish job listings.")
        return redirect('dashboard')

    # Verify that the recruiter has created at least one company page
    companies = Company.objects.filter(owner=request.user)
    if not companies.exists():
        messages.warning(
            request, 
            "You must register a Company Profile before publishing job vacancies. "
            "Please register a company in the Django Admin or company directory first."
        )
        return redirect('dashboard')

    if request.method == 'POST':
        form = JobPostingForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"Successfully published job vacancy: {job.title}!")
            return redirect('jobs')
        else:
            messages.error(request, "Failed to publish job opening. Please check form inputs.")
    else:
        form = JobPostingForm(user=request.user)

    return render(request, 'jobs/job-posting.html', {
        'form': form
    })

@login_required
def apply_job(request, job_id):
    """
    Handles candidate job submissions, verifies duplicate check, and uploads files.
    """
    if not request.user.is_candidate:
        messages.error(request, "Only candidates are authorized to apply for jobs.")
        return redirect('job_details', job_id=job_id)

    job = get_object_or_404(Job, pk=job_id)

    # Double application lock
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, "You have already applied to this job listing.")
        return redirect('job_details', job_id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            messages.success(request, f"Successfully submitted application for {job.title}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to submit application. Please verify file uploads.")
    
    return redirect('job_details', job_id=job_id)

@login_required
def update_application_status(request, application_id):
    """
    Recruiter-only controller to manage candidate pipeline stages.
    """
    if not request.user.is_recruiter:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    application = get_object_or_404(JobApplication, pk=application_id)

    # Verify company ownership
    if application.job.company.owner != request.user:
        messages.error(request, "You are unauthorized to update the candidate status for this posting.")
        return redirect('dashboard')

    if request.method == 'POST':
        status = request.POST.get('status', '').strip()
        if status in dict(JobApplication.STATUS_CHOICES):
            application.status = status
            application.save()
            messages.success(
                request, 
                f"Updated status for {application.applicant.get_full_name() or application.applicant.username} "
                f"to '{application.get_status_display()}'."
            )
        else:
            messages.error(request, "Invalid status choice selected.")

    return redirect('dashboard')
