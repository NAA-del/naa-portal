import os

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
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

# --- Authentication Views ---

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = NAAUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to the Academy.")
            
            # If student, nudge them to profile to complete details
            if user.membership_tier == 'student':
                messages.info(request, "Please complete your student profile details.")
                return redirect('profile')
                
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = NAAUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}!")
                redirect_url = request.GET.get('next', 'home')
                return redirect(redirect_url)
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

# --- Main Views ---

def home(request):
    announcements = Announcement.objects.all().order_by('-date_posted')
    leaders = Leader.objects.all()
    
    context = {
        'announcements': announcements,
        'leaders': leaders,
    }
    
    return render(request, 'accounts/home.html', context)

def about(request):
    about_info = AboutPage.objects.first()
    
    if not about_info:
        about_info = {
            'title': 'About the Academy',
            'history_text': 'History content pending...',
            'mission': 'Mission statement pending...',
            'vision': 'Vision statement pending...',
            'aims_and_objectives': 'Objectives pending...',
        }
        
    return render(request, 'accounts/about.html', {'about': about_info})

@login_required
def profile(request):
    # 1. Handle Profile Picture Update
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        p_form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Profile picture updated!")
            return redirect('profile')
    else:
        p_form = ProfilePictureForm(instance=request.user)

    # 2. Handle Student Profile Update (Only for students)
    
    # FIX: Use a direct database query to find the profile. 
    # This guarantees we find it if it exists, regardless of related_name.
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    
    if request.user.membership_tier == 'student':
        # Check if the POST request is meant for the Student Form (by checking a field name)
        if request.method == 'POST' and 'matric_number' in request.POST:
            if student_profile:
                s_form = StudentProfileForm(request.POST, instance=student_profile)
            else:
                s_form = StudentProfileForm(request.POST)
            
            if s_form.is_valid():
                student_obj = s_form.save(commit=False)
                student_obj.user = request.user
                student_obj.save()
                messages.success(request, "Student details updated!")
                return redirect('profile')
        else:
            s_form = StudentProfileForm(instance=student_profile) if student_profile else StudentProfileForm()
    else:
        s_form = None

    context = {
        'p_form': p_form,
        's_form': s_form,
        'student_profile': student_profile
    }
    return render(request, 'accounts/profile.html', context)

def download_constitution(request):
    file_path = os.path.join(settings.STATIC_ROOT, 'docs/NAA_Constitution.pdf')
    if not os.path.exists(file_path):
        file_path = os.path.join(settings.BASE_DIR, 'static/docs/NAA_Constitution.pdf')

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='NAA_Constitution.pdf')
    else:
        raise Http404("Constitution file not found")

@login_required
def resource_library(request):
    resources = Resource.objects.filter(is_public=True)
    if request.user.is_verified:
        private_resources = Resource.objects.filter(is_public=False)
        resources = resources | private_resources
    
    return render(request, 'accounts/resources.html', {
        'resources': resources.order_by('-uploaded_at')
    })

@login_required
def member_id_card(request):
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    
    if request.user.membership_tier == 'student' and not student_profile:
        # Ensure 'profile' is the correct name in your urls.py
        messages.error(request, "Action Required: Complete your Student Profile to view your ID.")
        return redirect('profile')

    return render(request, 'accounts/member_id.html', {
        'user': request.user, # Template uses {{ user }}
        'student_profile': student_profile, # Template uses {{ student_profile }}
        'expiry_date': 'December 2026'
    })

@login_required
def student_hub(request):
    # 1. Security: Only students allowed
    if request.user.membership_tier != 'student':
        messages.warning(request, "This section is for Student Members only.")
        return redirect('profile')

    # 2. LOCK: Check if profile is complete (Safe Query)
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    
    if not student_profile:
        messages.error(request, "Action Required: Please complete your Student Details (University & Matric No) to access the Student Hub.")
        return redirect('profile')

    # 3. Filter Logic
    announcements = StudentAnnouncement.objects.all().order_by('-date_posted')
    if student_profile:
        announcements = announcements.filter(
            target_university__in=['All', student_profile.university]
        )
    else:
        announcements = announcements.filter(target_university='All')

    return render(request, 'accounts/student_hub.html', {
        'announcements': announcements
    })

@login_required
def cpd_tracker(request):
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