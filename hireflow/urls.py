"""
URL configuration for hireflow project.
"""
from django.contrib import admin
from django.urls import path
from django.views.static import serve
from django.conf import settings
import home.views
import jobs.views
import companies.views
import accounts.views
import contact.views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Production Standard Views
    path('', home.views.index, name='index'),
    path('about/', home.views.about, name='about'),
    path('contact/', contact.views.contact, name='contact'),
    path('jobs/', jobs.views.jobs, name='jobs'),
    path('jobs/details/', jobs.views.job_details, name='job_details_default'),
    path('jobs/<int:job_id>/', jobs.views.job_details, name='job_details'),
    path('jobs/post/', jobs.views.job_posting, name='job_posting'),
    path('companies/', companies.views.companies, name='companies'),
    
    # Accounts Views
    path('accounts/login/', accounts.views.login, name='login'),
    path('accounts/register/', accounts.views.register, name='register'),
    path('accounts/recruiter-login/', accounts.views.recruiter_login, name='recruiter_login'),
    path('accounts/candidate-login/', accounts.views.candidate_login, name='candidate_login'),
    path('accounts/dashboard/', accounts.views.dashboard, name='dashboard'),
    path('accounts/saved-jobs/', accounts.views.saved_jobs, name='saved_jobs'),
    path('accounts/logout/', accounts.views.logout_view, name='logout'),


    # 2. Static HTML Path Fallbacks (Ensures template navigation links do not break)
    path('home/templates/home/index.html', home.views.index),
    path('home/templates/home/about.html', home.views.about),
    path('contact/templates/contact/contact.html', contact.views.contact),
    path('jobs/templates/jobs/jobs.html', jobs.views.jobs),
    path('jobs/templates/jobs/job-details.html', jobs.views.job_details),
    path('jobs/templates/jobs/job-posting.html', jobs.views.job_posting),
    path('companies/templates/companies/companies.html', companies.views.companies),
    path('accounts/templates/accounts/login.html', accounts.views.login),
    path('accounts/templates/accounts/register.html', accounts.views.register),
    path('accounts/templates/accounts/recruiter-login.html', accounts.views.recruiter_login),
    path('accounts/templates/accounts/candidate-login.html', accounts.views.candidate_login),
    path('accounts/templates/accounts/dashboard.html', accounts.views.dashboard),
    path('accounts/templates/accounts/saved-jobs.html', accounts.views.saved_jobs),

    # 3. Dynamic Static Resource serving fallback (For local app/static pathing support)
    path('<str:app_name>/static/<path:path>', serve, {'document_root': settings.BASE_DIR}),
]
