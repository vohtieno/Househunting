import re

from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import OwnerVerification, User

PHONE_RE = re.compile(r"^(?:0|\+?254)[17]\d{8}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


class RegisterForm(forms.Form):
    ROLE_CHOICES = [
        ("TENANT", "Tenant"),
        (User.Role.OWNER, "Owner"),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)
    username = forms.CharField(max_length=30)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    preferred_location = forms.CharField(max_length=100, required=False)
    budget = forms.DecimalField(max_digits=12, decimal_places=2, min_value=100, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if not USERNAME_RE.match(username):
            raise forms.ValidationError("Use 3-30 letters, numbers, dots, underscores, or hyphens.")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def clean_phone(self):
        phone = re.sub(r"\s+", "", self.cleaned_data["phone"].strip())
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Enter a valid Kenyan mobile number.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        if password:
            candidate_user = User(
                username=cleaned_data.get("username", ""),
                email=cleaned_data.get("email", ""),
            )
            validate_password(password, user=candidate_user)

        return cleaned_data


class VerifyEmailForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class OwnerVerificationForm(forms.ModelForm):
    class Meta:
        model = OwnerVerification
        fields = ["national_id", "title_deed_ref", "property_address", "document"]