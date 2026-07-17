from django.shortcuts import render
from jobs.models import Job
from companies.models import Company

def index(request):
    """
    Renders the homepage displaying the latest 6 featured jobs and top 3 featured companies.
    """
    # Fetch the 6 most recent job postings using select_related for optimized SQL execution
    featured_jobs = Job.objects.select_related('company').order_by('-posted_date')[:6]
    # Fetch top 3 companies to display on landing page
    featured_companies = Company.objects.all()[:3]

    return render(request, 'home/index.html', {
        'featured_jobs': featured_jobs,
        'featured_companies': featured_companies
    })

def about(request):
    """
    Renders the company About page.
    """
    return render(request, 'home/about.html')
