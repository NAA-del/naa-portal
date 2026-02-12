"""
Django forms for the NAA application.

This module contains all form classes for user registration, profile management,
CPD tracking, committee operations, and public interactions.
"""

import re
from datetime import date

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from django_ckeditor_5.widgets import CKEditor5Widget

from .models import (
    User,
    StudentProfile,
    CPDRecord,
    CommitteeReport,
    CommitteeAnnouncement,
    Article,
)


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def clean_phone_number(phone):
    """
    Normalize and validate Nigerian phone numbers.
    
    Accepts formats: +2348012345678 or 08012345678
    Returns cleaned phone number or raises ValidationError.
    """
    if not phone:
        return phone
    
    # Remove formatting characters
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Validate format
    if not re.match(r"^(\+234|0)\d{10}$", phone):
        raise ValidationError(
            "Phone number must be in format: +2348012345678 or 08012345678"
        )
    
    return phone


# ============================================================================
# USER AUTHENTICATION & REGISTRATION FORMS
# ============================================================================

class NAAUserCreationForm(UserCreationForm):
    """Enhanced user registration form with comprehensive validation."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "your.email@example.com"
            }
        ),
    )

    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+2348012345678"
            }
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
                attrs={
                    "class": "form-control",
                    "placeholder": "Choose a username"
                }
            ),
            "membership_tier": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def clean_username(self):
        """Validate username format and uniqueness."""
        username = self.cleaned_data.get("username")

        # Check uniqueness (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")

        # Validate format
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", username):
            raise ValidationError(
                "Username must be 3-30 characters and can only contain "
                "letters, numbers, and underscores."
            )

        return username

    def clean_email(self):
        """Validate email uniqueness and block disposable domains."""
        email = self.cleaned_data.get("email").lower()

        # Check uniqueness
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
        """Validate and normalize phone number."""
        return clean_phone_number(self.cleaned_data.get("phone_number"))

    def clean(self):
        """Cross-field validation for passwords and username."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        username = cleaned_data.get("username")

        # Ensure passwords match
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        # Ensure password doesn't contain username
        if username and password1:
            if username.lower() in password1.lower():
                raise ValidationError(
                    {"password1": "Password cannot contain your username."}
                )

        return cleaned_data

    def save(self, commit=True):
        """Save user with normalized email."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].lower()

        if commit:
            user.save()

        return user


class UserUpdateForm(forms.ModelForm):
    """Form for updating user profile information."""

    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your first name"
            }
        ),
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter your last name"
            }
        ),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class ProfilePictureForm(forms.ModelForm):
    """Form for uploading/updating user profile picture."""

    class Meta:
        model = User
        fields = ["profile_picture"]
        widgets = {
            "profile_picture": forms.FileInput(
                attrs={"class": "form-control"}
            )
        }


# ============================================================================
# STUDENT PROFILE FORMS
# ============================================================================

class StudentProfileForm(forms.ModelForm):
    """Form for creating and updating student profiles."""

    class Meta:
        model = StudentProfile
        fields = ["university", "matric_number", "level"]
        widgets = {
            "university": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True
                }
            ),
            "matric_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., UNIMED/AUD/2024/001",
                    "required": True,
                }
            ),
            "level": forms.Select(
                attrs={
                    "class": "form-select",
                    "required": True
                }
            ),
        }

    def clean_matric_number(self):
        """Validate matriculation number format and uniqueness."""
        matric = self.cleaned_data.get("matric_number")

        if matric:
            # Normalize: uppercase and remove spaces
            matric = matric.replace(" ", "").upper()

            # Check uniqueness (excluding current instance)
            existing = StudentProfile.objects.filter(matric_number__iexact=matric)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError(
                    "This matriculation number is already registered."
                )

            # Validate format
            if not re.match(r"^[A-Z0-9/]{5,30}$", matric):
                raise ValidationError(
                    "Invalid matric number format. Use letters, numbers, and slashes only."
                )

        return matric


# ============================================================================
# CPD (CONTINUING PROFESSIONAL DEVELOPMENT) FORMS
# ============================================================================

class CPDSubmissionForm(forms.ModelForm):
    """Form for submitting CPD activity records."""

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
                    "max": date.today().isoformat(),
                }
            ),
            "points": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 50,
                    "value": 5
                }
            ),
            "certificate": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf"
                }
            ),
        }

    def clean_activity_name(self):
        """Validate activity name length."""
        name = self.cleaned_data.get("activity_name")

        if len(name) < 5:
            raise ValidationError("Activity name is too short (minimum 5 characters).")

        if len(name) > 255:
            raise ValidationError("Activity name is too long (maximum 255 characters).")

        return name

    def clean_date_completed(self):
        """Ensure activity date is not in the future."""
        date_completed = self.cleaned_data.get("date_completed")

        if date_completed and date_completed > date.today():
            raise ValidationError("Activity date cannot be in the future.")

        return date_completed

    def clean_points(self):
        """Validate CPD points are within acceptable range."""
        points = self.cleaned_data.get("points")

        if points < 1:
            raise ValidationError("Points must be at least 1.")

        if points > 50:
            raise ValidationError("Points cannot exceed 50 per activity.")

        return points


# ============================================================================
# COMMITTEE FORMS
# ============================================================================

class CommitteeReportForm(forms.ModelForm):
    """Form for uploading committee reports."""

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
            "file": forms.FileInput(
                attrs={"class": "form-control"}
            ),
        }


class CommitteeAnnouncementForm(forms.ModelForm):
    """Form for creating committee announcements."""

    class Meta:
        model = CommitteeAnnouncement
        fields = ["title", "content"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),
        }


# ============================================================================
# CONTENT FORMS
# ============================================================================

class ArticleSubmissionForm(forms.ModelForm):
    """Form for submitting articles with rich text content."""

    class Meta:
        model = Article
        fields = ["title", "image", "content"]
        widgets = {
            "content": CKEditor5Widget(config_name="default"),
        }


# ============================================================================
# PUBLIC FORMS
# ============================================================================

class ContactForm(forms.Form):
    """Form for public contact messages."""

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Your Name"
            }
        ),
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "your.email@example.com"
            }
        )
    )
    
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+2348012345678 (Optional)"
            }
        ),
    )
    
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Subject of your message"
            }
        ),
    )
    
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Your message"
            }
        )
    )

    def clean_phone_number(self):
        """Validate and normalize phone number (optional field)."""
        phone = self.cleaned_data.get("phone_number")
        
        if not phone:
            return phone
        
        # Remove formatting
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Validate (more lenient - +234 prefix is optional)
        if not re.match(r"^(\+234|0)?\d{10}$", phone):
            raise ValidationError(
                "Phone number must be in format: +2348012345678 or 08012345678"
            )
        
        return phone