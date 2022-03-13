from django.contrib import messages
from django.contrib.auth.models import User, auth
from django.shortcuts import redirect, render

# Create your views here.


def register(request):
    """Function for handing user registration"""
    redirect_register_url = "/accounts/register"
    redirect_login_url = "/accounts/login"
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
            return redirect(redirect_register_url)
        else:
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect(redirect_register_url)
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
                return redirect(redirect_login_url)
    else:
        return render(request, template)


def login(request):
    """Function for handling user login"""
    redirect_login_url = "/accounts/login"
    redirect_login_success = "/"
    template = "accounts/login.html"

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(username=email, password=password)

        if user is None:
            messages.error(request, "Wrong credentials! Please try again.")
            return redirect(redirect_login_url)

        else:
            auth.login(request, user)
            messages.success(request, "Login successful!")
            return redirect(redirect_login_success)

    return render(request, template)


def forgot_password(request):
    template = "accounts/forgot_password.html"
    return render(request, template)


def logout(request):
    """Function for logging out the user"""
    redirect_url = "/accounts/login"
    auth.logout(request)
    return redirect(redirect_url)
