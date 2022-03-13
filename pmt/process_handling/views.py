from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import ProcessModel


# Create your views here.

@login_required(login_url="/accounts/login")
def view_process_models(request):
    """Function that renders view processes"""
    redirect_url = "/view_process_models"
    template = "process_handling/view_process_models.html"
    context = {}
    process_models = ProcessModel.objects.all()

    context["process_models"] = process_models
    return render(request, template, context)
