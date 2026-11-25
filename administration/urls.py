from django.urls import path

from . import views

app_name = "administration"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("users/<int:user_id>/toggle-active/", views.toggle_user_active_view, name="toggle_user_active"),
    path("users/<int:user_id>/toggle-verified/", views.toggle_document_verified_view, name="toggle_document_verified"),
    path("announcements/create/", views.create_announcement_view, name="create_announcement"),
    path("announcements/<int:announcement_id>/delete/", views.delete_announcement_view, name="delete_announcement"),
]