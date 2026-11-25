from django.conf import settings
from django.db import models


class Announcement(models.Model):
    class AudienceRole(models.TextChoices):
        ALL = "ALL", "All Users"
        CUSTOMER = "CUSTOMER", "Customers / Tenants"
        OWNER = "OWNER", "House Owners"

    title = models.CharField(max_length=150)
    message = models.TextField()
    audience_role = models.CharField(
        max_length=20,
        choices=AudienceRole.choices,
        default=AudienceRole.ALL,
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="announcements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title