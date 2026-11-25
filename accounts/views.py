from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, RegisterForm, VerifyEmailForm
from .models import EmailOTP, User


def _get_safe_next_url(request, fallback=None):
    next_url = request.POST.get("next") or request.GET.get("next") or fallback
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return None


def _send_verification_otp(user):
    otp = EmailOTP.generate_for_user(user)
    subject = "Verify your Househunting email address"
    message = (
        f"Hello {user.username},\n\n"
        f"Your Househunting verification code is: {otp.code}\n"
        f"This code expires in 15 minutes.\n\n"
        f"If you did not create an account, please ignore this email."
    )
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
    return otp


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    next_url = _get_safe_next_url(request)

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=data["role"],
                phone=data["phone"].strip(),
                preferred_location=(data.get("preferred_location") or "").strip(),
                budget=data.get("budget"),
                email_verified=False,
            )

            _send_verification_otp(user)
            request.session["pending_verification_user_id"] = user.id
            if next_url:
                request.session["post_verify_next_url"] = next_url

            messages.success(
                request,
                f"Account created! Enter the 6-digit code sent to {user.email} to verify your email.",
            )
            return redirect("accounts:verify_email")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {"form": form, "next": next_url or ""},
    )


def verify_email_view(request):
    user_id = request.session.get("pending_verification_user_id")
    if not user_id:
        messages.info(request, "Please sign up or log in to verify your email.")
        return redirect("accounts:login")

    user = get_object_or_404(User, id=user_id)
    saved_next = request.session.get("post_verify_next_url", "")

    if user.email_verified:
        request.session.pop("pending_verification_user_id", None)
        request.session.pop("post_verify_next_url", None)
        messages.info(request, "Your email is already verified. Please log in.")
        if saved_next:
            return redirect(f"/accounts/login/?next={saved_next}")
        return redirect("accounts:login")

    if request.method == "POST":
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"].strip()
            otp = EmailOTP.objects.filter(
                user=user,
                code=code,
                is_used=False,
            ).first()

            if otp is None:
                messages.error(request, "Invalid verification code.")
            elif otp.is_expired():
                messages.error(request, "This code has expired. Click 'Resend Code' for a new one.")
            else:
                otp.is_used = True
                otp.save(update_fields=["is_used"])

                user.email_verified = True
                user.save(update_fields=["email_verified"])

                request.session.pop("pending_verification_user_id", None)
                request.session.pop("post_verify_next_url", None)
                messages.success(request, "Email verified successfully! Please log in to continue.")
                if saved_next:
                    return redirect(f"/accounts/login/?next={saved_next}")
                return redirect("accounts:login")
    else:
        form = VerifyEmailForm()

    return render(
        request,
        "accounts/verify_email.html",
        {"form": form, "pending_user": user},
    )


def resend_otp_view(request):
    if request.method != "POST":
        return redirect("accounts:verify_email")

    user_id = request.session.get("pending_verification_user_id")
    if not user_id:
        messages.error(request, "No pending email verification found.")
        return redirect("accounts:login")

    user = get_object_or_404(User, id=user_id)
    _send_verification_otp(user)
    messages.success(request, f"A new verification code was sent to {user.email}.")
    return redirect("accounts:verify_email")


def login_view(request):
    next_url = _get_safe_next_url(request)

    if request.user.is_authenticated:
        if next_url:
            return redirect(next_url)
        if request.user.role == User.Role.ADMIN or request.user.is_superuser:
            return redirect("administration:dashboard")
        return redirect("dashboard:home")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"].strip()
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                is_admin = user.role == User.Role.ADMIN or user.is_superuser
                if not is_admin and not user.email_verified:
                    _send_verification_otp(user)
                    request.session["pending_verification_user_id"] = user.id
                    if next_url:
                        request.session["post_verify_next_url"] = next_url
                    messages.warning(
                        request,
                        "Please verify your email first. We sent a fresh code to your email.",
                    )
                    return redirect("accounts:verify_email")

                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")

                if next_url:
                    return redirect(next_url)
                if is_admin:
                    return redirect("administration:dashboard")
                return redirect("dashboard:home")

            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": next_url or ""},
    )


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("accounts:login")