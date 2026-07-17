from django.shortcuts import render
from .models import Company

def companies(request):
    """
    Renders the companies list page with support for name search queries.
    """
    companies_list = Company.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        companies_list = companies_list.filter(name__icontains=q)

    return render(request, 'companies/companies.html', {
        'companies': companies_list,
        'q': q
    })
