from django.shortcuts import render

def jobs(request):
    return render(request, 'jobs/jobs.html')

def job_details(request):
    return render(request, 'jobs/job-details.html')

def job_posting(request):
    return render(request, 'jobs/job-posting.html')
