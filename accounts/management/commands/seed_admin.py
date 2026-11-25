import os

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = "Seed the default administrator account from environment variables or defaults."

    def handle(self, *args, **options):
        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@househunting.local")
        password = os.getenv("ADMIN_PASSWORD", "admin123")
        phone = os.getenv("ADMIN_PHONE", "254700000000")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": User.Role.ADMIN,
                "phone": phone,
                "email_verified": True,
                "is_document_verified": True,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if not created:
            user.email = email
            user.role = User.Role.ADMIN
            user.phone = phone
            user.email_verified = True
            user.is_document_verified = True
            user.is_staff = True
            user.is_superuser = True

        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} admin account -> username: '{username}', email: '{email}', password: '{password}'"
            )
        )