from django.shortcuts import render

def login(request):
    return render(request, 'accounts/login.html')

def register(request):
    return render(request, 'accounts/register.html')

def recruiter_login(request):
    return render(request, 'accounts/recruiter-login.html')

def candidate_login(request):
    return render(request, 'accounts/candidate-login.html')

def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def saved_jobs(request):
    return render(request, 'accounts/saved-jobs.html')
