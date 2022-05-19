from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
# Create your views here.


def register(request):
    """Function for handing user registration"""
    template = "accounts/register.html"

    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        username = email
        password = request.POST["password"]
        repeat_password = request.POST["repeat_password"]

        # Check if password is same with repeat password, and email is unique then continue
        if password != repeat_password:
            messages.error(request, "Passwords must match!")
            return redirect(reverse_lazy("accounts:register"))
        else:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect(reverse_lazy("accounts:register"))
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.save()
                messages.success(request, "Account created successfully!")
                return redirect(reverse_lazy("accounts:login"))
    else:
        return render(request, template)


def login(request):
    """Function for handling user login"""
    template = "accounts/login.html"

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(username=email, password=password)

        if user is None:
            messages.error(request, "Wrong credentials! Please try again.")
            return redirect(reverse_lazy("accounts:login"))

        else:
            auth.login(request, user)
            messages.success(request, "Login successful!")
            return redirect(reverse_lazy("core:index"))

    return render(request, template)


def logout(request):
    """Function for logging out the user"""
    auth.logout(request)
    return redirect(reverse_lazy("accounts:login"))
