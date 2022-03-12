from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.contrib.auth.forms import UserCreationForm

from .forms import CreateUserForm
# Create your views here.
def register(request) -> HttpResponse:
    """View for handling user registration"""
    template = "accounts/register.html"
    register_form = CreateUserForm()

    if request.method == "POST":
        register_form = CreateUserForm(request.POST)
        if register_form.is_valid():
            register_form.save()


    context = {"register_form": register_form}

    return render(request, template, context)


def login(request) -> HttpResponse:
    """View for handling user login"""
    context = {}
    template = "accounts/login.html"
    return render(request, template, context)


def logout(request):
    """View for handling user logout"""
    pass
