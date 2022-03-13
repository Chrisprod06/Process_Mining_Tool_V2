from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.


def index(request) -> HttpResponse:
    """View that renders index page"""
    template = "core/index.html"
    context = {}
    return render(request, template, context)
