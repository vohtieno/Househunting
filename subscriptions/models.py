from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    duration_days = models.PositiveIntegerField()
    price_kes = models.DecimalField(max_digits=10, decimal_places=2)
    max_listings = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price_kes"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (KES {self.price_kes} / {self.duration_days}d)"


class UserSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="user_subscriptions",
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-end_date"]

    @property
    def is_valid(self):
        return self.is_active and timezone.now() <= self.end_date

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} (until {self.end_date:%Y-%m-%d})"