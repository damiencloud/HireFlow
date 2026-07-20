from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company
from .forms import CompanyForm
from jobs.models import Job

def companies(request):
    """
    Renders the companies directory list page with support for name search queries.
    """
    companies_list = Company.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        companies_list = companies_list.filter(name__icontains=q)

    return render(request, 'companies/companies.html', {
        'companies': companies_list,
        'q': q
    })

def company_details(request, company_id):
    """
    Public view displaying an individual company profile and its active job openings.
    """
    company = get_object_or_404(Company, pk=company_id)
    active_jobs = Job.objects.filter(company=company).order_by('-posted_date')
    
    return render(request, 'companies/company-details.html', {
        'company': company,
        'active_jobs': active_jobs
    })

@login_required
def create_company(request):
    """
    Recruiter-only view to register a new Company profile.
    Automatically assigns request.user as the company owner.
    """
    if not request.user.is_recruiter:
        messages.error(request, "Only recruiters are authorized to register company profiles.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.owner = request.user
            company.save()
            messages.success(request, f"Company profile '{company.name}' created successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to create company profile. Please check form errors below.")
    else:
        form = CompanyForm()

    return render(request, 'companies/company-form.html', {
        'form': form
    })

@login_required
def edit_company(request, company_id):
    """
    Recruiter-only view to update an existing Company profile.
    Verifies that the recruiter owns the company before allowing edits.
    """
    if not request.user.is_recruiter:
        messages.error(request, "Only recruiters are authorized to edit company profiles.")
        return redirect('dashboard')

    company = get_object_or_404(Company, pk=company_id)

    # Permission check: Ensure owner match
    if company.owner != request.user:
        messages.error(request, "You are not authorized to edit this company profile.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, f"Company profile '{company.name}' updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to update company profile. Please check form errors below.")
    else:
        form = CompanyForm(instance=company)

    return render(request, 'companies/company-form.html', {
        'form': form,
        'company': company
    })

@login_required
def delete_company(request, company_id):
    """
    Recruiter-only view to delete a Company profile.
    Verifies ownership before executing deletion.
    """
    if not request.user.is_recruiter:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    company = get_object_or_404(Company, pk=company_id)

    if company.owner != request.user:
        messages.error(request, "You are not authorized to delete this company profile.")
        return redirect('dashboard')

    if request.method == 'POST':
        name = company.name
        company.delete()
        messages.success(request, f"Company profile '{name}' was deleted successfully.")

    return redirect('dashboard')
