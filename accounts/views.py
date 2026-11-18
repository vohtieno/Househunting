from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import redirect, render

from .models import User


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role", "CUSTOMER")

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
            return render(request, "accounts/register.html")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "accounts/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "accounts/register.html")

        if role not in [
            User.Role.CUSTOMER,
            User.Role.OWNER,
            User.Role.AGENT,
        ]:
            role = User.Role.CUSTOMER

        user = User.objects.create(
            username=username,
            email=email,
            phone=phone,
            role=role,
            password=make_password(password),
        )

        login(request, user)

        messages.success(request, "Account created successfully.")

        return redirect("dashboard:home")

    return render(request, "accounts/register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)

            if user.role == User.Role.ADMIN:
                return redirect("administration:dashboard")

            return redirect("dashboard:home")

        messages.error(request, "Invalid username or password.")

    return render(request, "accounts/login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")