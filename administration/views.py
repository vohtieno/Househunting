from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import LoginForm, RegisterForm, VerifyEmailForm
from payments.models import MpesaTransaction
from properties.models import Property
from subscriptions.models import UserSubscription

from .models import Announcement

User = get_user_model()


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        user = request.user
        is_admin = getattr(user, "role", None) == User.Role.ADMIN or user.is_superuser or user.is_staff
        if not is_admin:
            messages.error(request, "You do not have permission to access the administration panel.")
            return redirect("dashboard:home")
        return view_func(request, *args, **kwargs)

    return _wrapped


@admin_required
def dashboard_view(request):
    query = (request.GET.get("q") or "").strip()

    users_qs = User.objects.order_by("-date_joined")
    properties_qs = (
        Property.objects.select_related("owner").order_by("-created_at")
        if hasattr(Property, "created_at")
        else Property.objects.select_related("owner").order_by("-id")
    )
    transactions_qs = MpesaTransaction.objects.select_related("user", "property", "plan").order_by("-created_at")
    announcements_qs = Announcement.objects.order_by("-id")

    if query:
        users_qs = users_qs.filter(
            Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
        )
        properties_qs = properties_qs.filter(
            Q(title__icontains=query) | Q(location__icontains=query)
        )

    total_users = User.objects.count()
    total_owners = User.objects.filter(role=User.Role.OWNER).count()
    total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_properties = Property.objects.count()
    active_subscriptions = UserSubscription.objects.count()

    completed_filter = Q(status__iexact="COMPLETED") | Q(status__iexact="SUCCESS") | Q(status__iexact="PAID")
    total_revenue = (
        MpesaTransaction.objects.filter(completed_filter).aggregate(total=Sum("amount_kes"))["total"] or 0
    )

    context = {
        "query": query,
        "users": users_qs[:20],
        "properties": properties_qs[:20],
        "transactions": transactions_qs[:20],
        "announcements": announcements_qs[:20],
        "total_users": total_users,
        "total_owners": total_owners,
        "total_customers": total_customers,
        "total_properties": total_properties,
        "active_subscriptions": active_subscriptions,
        "total_revenue": total_revenue,
        "login_form": LoginForm(),
        "register_form": RegisterForm(),
        "verify_form": VerifyEmailForm(),
    }
    return render(request, "administration/dashboard.html", context)


admin_dashboard = dashboard_view


@admin_required
def toggle_user_active_view(request, user_id):
    if request.method != "POST":
        return redirect("administration:dashboard")

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.warning(request, "You cannot deactivate your own account.")
        return redirect("administration:dashboard")

    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=["is_active"])
    state = "activated" if target_user.is_active else "deactivated"
    messages.success(request, f"User '{target_user.username}' has been {state}.")
    return redirect("administration:dashboard")


@admin_required
def toggle_document_verified_view(request, user_id):
    if request.method != "POST":
        return redirect("administration:dashboard")

    target_user = get_object_or_404(User, id=user_id)
    target_user.is_document_verified = not target_user.is_document_verified
    target_user.save(update_fields=["is_document_verified"])
    status_label = "verified" if target_user.is_document_verified else "unverified"
    messages.success(request, f"Documents for '{target_user.username}' marked as {status_label}.")
    return redirect("administration:dashboard")


@admin_required
def create_announcement_view(request):
    if request.method != "POST":
        return redirect("administration:dashboard")

    title = (request.POST.get("title") or "").strip()
    message = (request.POST.get("message") or "").strip()

    if not title or not message:
        messages.error(request, "Both an announcement title and message are required.")
        return redirect("administration:dashboard")

    create_kwargs = {"title": title, "message": message}
    if hasattr(Announcement, "created_by"):
        create_kwargs["created_by"] = request.user
    elif hasattr(Announcement, "author"):
        create_kwargs["author"] = request.user

    Announcement.objects.create(**create_kwargs)
    messages.success(request, "Announcement published.")
    return redirect("administration:dashboard")


@admin_required
def delete_announcement_view(request, announcement_id):
    if request.method != "POST":
        return redirect("administration:dashboard")

    announcement = get_object_or_404(Announcement, id=announcement_id)
    announcement.delete()
    messages.success(request, "Announcement deleted.")
    return redirect("administration:dashboard")