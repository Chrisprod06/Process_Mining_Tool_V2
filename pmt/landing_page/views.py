from django.shortcuts import render


# Create your views here.

def start_page(request):
    """View to render landing page for project"""
    template = "landing_page/landing.html"

    return render(request, template)
