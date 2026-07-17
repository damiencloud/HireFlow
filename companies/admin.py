from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'website', 'owner']
    search_fields = ['name', 'location', 'owner__username']
    list_filter = ['location']
