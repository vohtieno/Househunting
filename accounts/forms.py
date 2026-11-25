from django import forms
from django.contrib.auth.password_validation import validate_password

from .models import User


class RegisterForm(forms.Form):
    ROLE_CHOICES = [
        (User.Role.CUSTOMER, "Customer / Tenant"),
        (User.Role.OWNER, "House Owner"),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    preferred_location = forms.CharField(max_length=100, required=False)
    budget = forms.DecimalField(max_digits=12, decimal_places=2, required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("That username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        if password:
            validate_password(password)

        return cleaned_data


class VerifyEmailForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)