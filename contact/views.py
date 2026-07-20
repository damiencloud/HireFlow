from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact(request):
    """
    Renders the Contact Us page and handles support message form submissions.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been submitted successfully! We will get back to you soon.")
            return redirect('contact')
        else:
            messages.error(request, "Failed to submit message. Please correct the form errors below.")
    else:
        form = ContactForm()

    return render(request, 'contact/contact.html', {'form': form})
