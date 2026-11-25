import random
import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):

    class Role(models.TextChoices):
        CUSTOMER = "CUSTOMER", "Customer / Tenant"
        OWNER = "OWNER", "House Owner"
        ADMIN = "ADMIN", "Administrator"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    preferred_location = models.CharField(
        max_length=100,
        blank=True,
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )

    email_verified = models.BooleanField(
        default=False,
    )

    is_document_verified = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def normalized_phone(self):
        digits = re.sub(r"\D", "", self.phone or "")
        if digits.startswith("254") and len(digits) == 12:
            return digits
        if digits.startswith("0") and len(digits) == 10:
            return "254" + digits[1:]
        if len(digits) == 9 and digits.startswith(("7", "1")):
            return "254" + digits
        return digits

    def has_active_subscription(self):
        return self.subscriptions.filter(
            is_active=True,
            end_date__gte=timezone.now(),
        ).exists()

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"


class EmailOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_otps",
    )
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def generate_for_user(cls, user, valid_minutes=15):
        cls.objects.filter(user=user, is_used=False).update(is_used=True)
        code = f"{random.randint(0, 999999):06d}"
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=valid_minutes),
        )

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"OTP for {self.user.username} ({self.code})"