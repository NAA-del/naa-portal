import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from django.conf import settings
from django.http import FileResponse, Http404

# 1. IMPORT ALL MODELS
from .models import (
    User, AboutPage, Announcement, Leader, 
    Resource, StudentProfile, StudentAnnouncement, CPDRecord
)

# 2. IMPORT ALL FORMS
from .forms import (
    NAAUserCreationForm, StudentProfileForm, ProfilePictureForm, CPDSubmissionForm
)

def home(request):
    announcements = Announcement.objects.all().order_by('-date_posted')
    leaders = Leader.objects.all()
    
    # Check carefully: The dictionary starts with { and ends with }
    context = {
        'announcements': announcements,
        'leaders': leaders,
    }
    
    return render(request, 'accounts/home.html', context)

def about(request):
    # Fetch the very first entry in the AboutPage table
    about_info = AboutPage.objects.first()
    
    # If the database is empty, create a temporary 'fake' object 
    # so the page doesn't crash while you are testing
    if not about_info:
        about_info = {
            'title': 'About NAA',
            'history_text': 'Please add history in Admin.',
            'mission': 'Please add mission in Admin.',
            'vision': 'Please add vision in Admin.',
            'aims_and_objectives': 'Objective 1\nObjective 2'
        }

    return render(request, 'accounts/about.html', {'about': about_info})

def register(request):
    if request.method == 'POST':
        form = NAAUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login to complete your profile.")
            return redirect('login') # We will create the login page next
    else:
        form = NAAUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                
                # SMART REDIRECT LOGIC
                # 1. If student, send to Student Hub
                if user.membership_tier == 'student':
                    return redirect('student_hub')
                
                # 2. If professional, send to Profile
                return redirect('profile')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# accounts/views.py
@login_required
def profile(request):
    try:
        student_profile = request.user.student_info
    except StudentProfile.DoesNotExist:
        student_profile = None

    if request.method == 'POST':
        # Handle Photo Upload
        if 'upload_photo' in request.POST:
            photo_form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
            if photo_form.is_valid():
                photo_form.save()
                messages.success(request, "Profile picture updated!")
                return redirect('profile')
        
        # Handle Academic Info
        else:
            form = StudentProfileForm(request.POST)
            if form.is_valid() and not student_profile:
                new_profile = form.save(commit=False)
                new_profile.user = request.user
                new_profile.save()
                messages.success(request, "Academic details locked and saved!")
                return redirect('profile')
    
    form = StudentProfileForm(instance=student_profile)
    photo_form = ProfilePictureForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'photo_form': photo_form,
        'student_profile': student_profile
    })

@login_required
def student_hub(request):
    if request.user.membership_tier != 'student':
        return redirect('home')

    # This line counts students per school - requires the import above!
    stats = StudentProfile.objects.values('university').annotate(total=Count('university'))
    student_resources = Resource.objects.filter(category='student')
    announcements = StudentAnnouncement.objects.order_by('-date_posted')[:5]
    
    context = {
        'resources': student_resources,
        'stats': stats,
        'announcements': announcements,
        'is_verified': request.user.is_verified
    }
    return render(request, 'accounts/student_hub.html', context)

# 1. The Secure Constitution Download View
@login_required
def download_constitution(request):
    # Only Verified members can download (Section 6 Compliance)
    if not request.user.is_verified:
        return render(request, 'accounts/profile.html', {
            'error': 'Access Denied: Your account must be verified to download the Constitution.'
        })
    
    file_path = os.path.join(settings.BASE_DIR, 'static', 'docs', 'constitution.pdf')
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    else:
        print(f"DEBUG: Looked for PDF at {file_path}")
        raise Http404("The Constitution PDF is missing from the static/docs/ folder.")

@login_required
def resource_library(request):
    # 1. Start with resources that are marked as Public
    resources = Resource.objects.filter(is_public=True)
    
    # 2. If user is logged in AND verified, add the restricted resources
    if request.user.is_authenticated and request.user.is_verified:
        private_resources = Resource.objects.filter(is_public=False)
        resources = resources | private_resources  # This combines both lists
    
    return render(request, 'accounts/resources.html', {
        'resources': resources.order_by('-uploaded_at')
    })

@login_required
def member_id_card(request):
    # If the user is a student, we want to show their university info too
    student_info = getattr(request.user, 'student_info', None)
    
    return render(request, 'accounts/member_id.html', {
        'member': request.user,
        'student_info': student_info,
        'expiry_date': 'December 2026' # You can make this dynamic later
    })

@login_required
def cpd_tracker(request):
    # Only show records for the logged-in user
    records = request.user.cpd_records.all().order_by('-date_completed')
    total_points = sum(record.points for record in records)

    if request.method == 'POST':
        form = CPDSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            new_record = form.save(commit=False)
            new_record.user = request.user
            new_record.save()
            messages.success(request, "CPD activity recorded successfully!")
            return redirect('cpd_tracker')
    else:
        form = CPDSubmissionForm()

    return render(request, 'accounts/cpd_tracker.html', {
        'records': records,
        'total_points': total_points,
        'form': form
    })