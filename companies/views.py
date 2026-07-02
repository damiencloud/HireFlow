from django.shortcuts import render

def companies(request):
    return render(request, 'companies/companies.html')
