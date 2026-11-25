from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.forms import OwnerVerificationForm
from accounts.models import OwnerVerification, User
from properties.models import Property


def verified_owner_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if user.role != User.Role.OWNER and not user.is_superuser:
            return redirect("dashboard:home")
        if not user.is_document_verified and not user.is_superuser:
            messages.warning(
                request,
                "Submit your National ID, Chief phone number, Title Deed, and house document to unlock this section.",
            )
            return redirect("dashboard:home")
        return view_func(request, *args, **kwargs)

    return _wrapped


@login_required
def owner_dashboard_view(request):
    user = request.user
    if user.role == User.Role.ADMIN or user.is_superuser:
        return redirect("administration:dashboard")

    verification = OwnerVerification.objects.filter(user=user).first()
    is_verified = bool(user.is_document_verified)

    if request.method == "POST":
        form = OwnerVerificationForm(request.POST, request.FILES, instance=verification)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = user
            record.status = OwnerVerification.Status.PENDING
            record.save()
            messages.success(
                request,
                "Verification details and documents submitted. Navigation links remain locked until verified.",
            )
            return redirect("dashboard:home")
    else:
        form = OwnerVerificationForm(instance=verification)

    properties_qs = Property.objects.filter(owner=user) if is_verified else Property.objects.none()

    context = {
        "is_verified": is_verified,
        "verification": verification,
        "verification_form": form,
        "properties": properties_qs,
        "active_nav": "overview",
    }
    return render(request, "dashboard/owner_dashboard.html", context)


home = owner_dashboard_view