from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.

@login_required(login_url="accounts/login")
def index(request) -> HttpResponse:
    """View that renders index page"""
    template = "core/index.html"
    context = {}
    return render(request, template, context)
