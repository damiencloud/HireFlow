from django.contrib import admin
from .models import Job, JobApplication

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'category', 'job_type', 'experience_level', 'posted_date']
    search_fields = ['title', 'company__name', 'location']
    list_filter = ['category', 'job_type', 'experience_level', 'posted_date']
    date_hierarchy = 'posted_date'

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'applied_date']
    search_fields = ['applicant__username', 'job__title', 'job__company__name']
    list_filter = ['status', 'applied_date']
    date_hierarchy = 'applied_date'
