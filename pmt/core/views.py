from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import ChangePasswordForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password

# Create your views here.


@login_required(login_url="accounts/login")
def index(request) -> HttpResponse:
    """View that renders index page"""
    template = "core/index.html"
    context = {}
    return render(request, template, context)


@login_required(login_url="accounts/login")
def change_password(request, pk):
    """View that handles user details change"""
    template = "core/change_password_form.html"
    current_user = User.objects.get(pk=pk)

    current_user_changed = User(pk=current_user.pk,
                                username=current_user.username,
                                password=current_user.password,
                                email=current_user.email,
                                first_name=current_user.first_name,
                                last_name=current_user.last_name)
    change_password_form = ChangePasswordForm()

    if request.method == "POST":
        change_password_form = ChangePasswordForm(request.POST)
        if change_password_form.is_valid():
            password = change_password_form.cleaned_data["password"]
            password_confirm = change_password_form.cleaned_data["password_confirm"]
            if password != password_confirm:
                messages.error(request, "Passwords must match!")
                return redirect(reverse_lazy("core:change_password", kwargs={"pk": pk}))
            else:
                current_user_changed.password = make_password(password)
                current_user_changed.save()
                messages.success(request, "Password changed successfully!")

    context = {
        "change_password_form": change_password_form
    }
    return render(request, template, context)
