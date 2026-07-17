from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CandidateProfile, RecruiterProfile

class CustomUserAdmin(UserAdmin):
    """
    Extends standard Django UserAdmin to display custom role flags.
    """
    model = CustomUser
    list_display = ['username', 'email', 'is_candidate', 'is_recruiter', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Configuration', {'fields': ('is_candidate', 'is_recruiter')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Configuration', {'fields': ('is_candidate', 'is_recruiter')}),
    )

# Register CustomUser with Extended UserAdmin layout
admin.site.register(CustomUser, CustomUserAdmin)

# Register profiles with custom columns in list view
@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'skills']
    search_fields = ['user__username', 'skills']

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name']
    search_fields = ['user__username', 'company_name']
