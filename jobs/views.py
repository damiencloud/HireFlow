from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job
from .forms import JobPostingForm
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
    Displays the details of a single job. Falls back to first job if no ID matches.
    """
    if job_id is None:
        job = Job.objects.first()
        if not job:
            messages.info(request, "No job vacancies listed yet.")
            return redirect('index')
    else:
        job = get_object_or_404(Job, pk=job_id)
        
    return render(request, 'jobs/job-details.html', {
        'job': job
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
