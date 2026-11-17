from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [

    # Main website and authentication
    path(
        "",
        include("core.urls")
    ),

    # User accounts
    path(
        "accounts/",
        include("accounts.urls")
    ),

    # Properties and listings
    path(
        "properties/",
        include("properties.urls")
    ),

    # Subscriptions
    path(
        "subscriptions/",
        include("subscriptions.urls")
    ),

    # Payments
    path(
        "payments/",
        include("payments.urls")
    ),

    # Customer inquiries
    path(
        "inquiries/",
        include("inquiries.urls")
    ),

    # Customer/Owner dashboards
    path(
        "dashboard/",
        include("dashboard.urls")
    ),

    # OUR CUSTOM ADMINISTRATION
    path(
        "administration/",
        include("administration.urls")
    ),
]


# Serve uploaded media during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )