from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import StudentProfile, CPDRecord, CommitteeReport, CommitteeAnnouncement, Article

class NAAUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        # Added phone_number and membership_tier to the standard fields
        fields = ['username', 'email', 'phone_number', 'membership_tier']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'membership_tier': forms.Select(attrs={'class': 'form-select'}),
        }

    # accounts/forms.py

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use .get() to avoid crashing if the password isn't there
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
    
class StudentProfileForm(forms.ModelForm):
    class Meta:  # <--- Change this from __clat__ to Meta
        model = StudentProfile
        fields = ['university', 'matric_number', 'level']
        
        # Adding Bootstrap styling to the form fields
        widgets = {
            'university': forms.Select(attrs={'class': 'form-select'}),
            'matric_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. UNIMED/AUD/2024/001'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
        }

# accounts/forms.py
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }

class CPDSubmissionForm(forms.ModelForm):
    class Meta:
        model = CPDRecord
        fields = ['activity_name', 'date_completed', 'points', 'certificate']
        widgets = {
            'activity_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Activity Name'}),
            'date_completed': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'certificate': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
class CommitteeReportForm(forms.ModelForm):
    class Meta:
        model = CommitteeReport
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Monthly Report - Jan 2026'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
class CommitteeAnnouncementForm(forms.ModelForm):
    class Meta:
        model = CommitteeAnnouncement
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ArticleSubmissionForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'image', 'content']
        widgets = {
            'content': CKEditor5Widget(config_name='default'),
        }
        
class UserUpdateForm(forms.ModelForm):
    # We add these two lines to make sure they show up on the profile page
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name',] # Add them to the fields list