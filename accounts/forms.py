from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import StudentProfile, CPDRecord

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
        fields = ['activity_name', 'points', 'date_completed', 'certificate']
        widgets = {
            'date_completed': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'activity_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Annual NAA Conference'}),
            'points': forms.NumberInput(attrs={'class': 'form-control'}),
            'certificate': forms.FileInput(attrs={'class': 'form-control'}),
        }