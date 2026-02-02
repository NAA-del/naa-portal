from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from datetime import date
from django_ckeditor_5.widgets import CKEditor5Widget
from django.core.exceptions import ValidationError
from .models import (
    StudentProfile,
    CPDRecord,
    CommitteeReport,
    CommitteeAnnouncement,
    Article,
)


class NAAUserCreationForm(UserCreationForm):
    """Enhanced registration form with validation"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "your.email@example.com"}
        ),
    )

    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+2348012345678"}
        ),
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "phone_number",
            "membership_tier",
            "password1",
            "password2",
        ]
        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Choose a username"}
            ),
            "membership_tier": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_username(self):
        """Validate username"""
        username = self.cleaned_data.get("username")

        # Check if username already exists (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")

        # Check format
        import re

        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", username):
            raise ValidationError(
                "Username must be 3-30 characters and can only contain "
                "letters, numbers, and underscores."
            )

        return username

    def clean_email(self):
        """Validate email"""
        email = self.cleaned_data.get("email").lower()

        # Check if email already exists
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email address is already registered.")

        # Block disposable email domains
        disposable_domains = [
            "tempmail.com",
            "guerrillamail.com",
            "10minutemail.com",
            "throwaway.email",
            "mailinator.com",
        ]

        domain = email.split("@")[1] if "@" in email else ""
        if domain in disposable_domains:
            raise ValidationError("Please use a permanent email address.")

        return email

    def clean_phone_number(self):
        """Validate and normalize phone number"""
        phone = self.cleaned_data.get("phone_number")

        if phone:
            # Remove spaces, dashes, parentheses
            phone = (
                phone.replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
            )

            # Ensure it starts with +234 or 0
            import re

            if not re.match(r"^(\+234|0)\d{10}$", phone):
                raise ValidationError(
                    "Phone number must be in format: +2348012345678 or 08012345678"
                )

        return phone

    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        username = cleaned_data.get("username")

        # Ensure passwords match
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        # Ensure password isn't too similar to username
        if username and password1:
            if username.lower() in password1.lower():
                raise ValidationError(
                    {"password1": "Password cannot contain your username."}
                )

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()

        if commit:
            user.save()

        return user


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ["university", "matric_number", "level"]
        widgets = {
            "university": forms.Select(
                attrs={"class": "form-select", "required": True}
            ),
            "matric_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., UNIMED/AUD/2024/001",
                    "required": True,
                }
            ),
            "level": forms.Select(attrs={"class": "form-select", "required": True}),
        }

    def clean_matric_number(self):
        """Validate matric number format"""
        matric = self.cleaned_data.get("matric_number")

        if matric:
            # Convert to uppercase and remove spaces
            matric = matric.replace(" ", "").upper()

            # Check if it already exists (excluding current instance)
            existing = StudentProfile.objects.filter(matric_number__iexact=matric)

            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError(
                    "This matriculation number is already registered."
                )

            # Basic format validation
            import re

            if not re.match(r"^[A-Z0-9/]{5,30}$", matric):
                raise ValidationError(
                    "Invalid matric number format. Use letters, numbers, and slashes only."
                )

        return matric


# accounts/forms.py
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["profile_picture"]
        widgets = {"profile_picture": forms.FileInput(attrs={"class": "form-control"})}


class CPDSubmissionForm(forms.ModelForm):
    class Meta:
        model = CPDRecord
        fields = ["activity_name", "date_completed", "points", "certificate"]
        widgets = {
            "activity_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., NAA Annual Conference 2026",
                    "maxlength": 255,
                }
            ),
            "date_completed": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                    "max": date.today().isoformat(),  # Can't be future date
                }
            ),
            "points": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 50, "value": 5}
            ),
            "certificate": forms.FileInput(
                attrs={"class": "form-control", "accept": ".pdf"}
            ),
        }

    def clean_activity_name(self):
        """Validate activity name"""
        name = self.cleaned_data.get("activity_name")

        if len(name) < 5:
            raise ValidationError("Activity name is too short.")

        if len(name) > 255:
            raise ValidationError("Activity name is too long (max 255 characters).")

        return name

    def clean_date_completed(self):
        """Ensure date is not in the future"""
        date_completed = self.cleaned_data.get("date_completed")

        if date_completed and date_completed > date.today():
            raise ValidationError("Activity date cannot be in the future.")

        return date_completed

    def clean_points(self):
        """Validate CPD points"""
        points = self.cleaned_data.get("points")

        if points < 1:
            raise ValidationError("Points must be at least 1.")

        if points > 50:
            raise ValidationError("Points cannot exceed 50 per activity.")

        return points


class CommitteeReportForm(forms.ModelForm):
    class Meta:
        model = CommitteeReport
        fields = ["title", "file"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Monthly Report - Jan 2026",
                }
            ),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }


class CommitteeAnnouncementForm(forms.ModelForm):
    class Meta:
        model = CommitteeAnnouncement
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ArticleSubmissionForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "image", "content"]
        widgets = {
            "content": CKEditor5Widget(config_name="default"),
        }


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your first name"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter your last name"}
        ),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class ContactForm(forms.Form):
    """Form for public contact messages."""

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "your.email@example.com"}
        )
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+2348012345678 (Optional)"}
        ),
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Subject of your message"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 5, "placeholder": "Your message"}
        )
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if phone:
            phone = (
                phone.replace(" ", "")
                .replace("-", "")
                .replace("(", "")
                .replace(")", "")
            )
            import re

            if not re.match(r"^(\+234|0)?\d{10}$", phone):
                raise ValidationError(
                    "Phone number must be in format: +2348012345678 or 08012345678"
                )
        return phone
