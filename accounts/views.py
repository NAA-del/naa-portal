import os
import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from datetime import datetime
from django.core.mail import send_mail
    
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MemberSerializer, CommitteeReportSerializer

# 1. IMPORT ALL MODELS
from .models import (
    User, AboutPage, Announcement, Leader, 
    Resource, StudentProfile, StudentAnnouncement, CPDRecord, Notification, Article, Committee, CommitteeReport,
    CommitteeAnnouncement
)

# 2. IMPORT ALL FORMS
from .forms import (
    NAAUserCreationForm, StudentProfileForm, ProfilePictureForm, CPDSubmissionForm, CommitteeReportForm,
    CommitteeAnnouncementForm, ArticleSubmissionForm
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
    announcements = Announcement.objects.filter(
        is_published=True
    ).order_by('-featured', '-date_posted')
    articles = Article.objects.filter(status='published', is_public=True).order_by('-created_at')[:3]

    leaders = Leader.objects.all()

    return render(request, 'accounts/home.html', {
        'announcements': announcements,
        'articles': articles,
        'leaders': leaders,
    })

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
        # Check if the POST request is meant for the Student Form
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
        'user': request.user,
        'p_form': p_form,
        's_form': s_form,
        'student_profile': student_profile
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def download_constitution(request):
    
    # Look for constitution.pdf in the primary static folder
    file_path = os.path.join(settings.BASE_DIR, 'static', 'constitution.pdf')
    
    # Fallback check if it was moved to a subfolder like static/docs/
    if not os.path.exists(file_path):
        file_path = os.path.join(settings.BASE_DIR, 'static', 'docs', 'constitution.pdf')

    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='NAA_Constitution.pdf')
    else:
        messages.error(request, "Constitution file is currently unavailable.")
        return redirect('home')

@login_required
def resource_library(request):
    user = request.user
    
    # 1. Define Tier Ranking for logic
    tier_rank = {
        'student': 1,
        'associate': 2,
        'full': 3,
        'fellow': 4
    }
    
    current_rank = tier_rank.get(user.membership_tier, 0)
    
    if not user.is_verified:
        resources = Resource.objects.filter(access_level='public')
    else:
        allowed_levels = ['public']
        if current_rank >= 1: allowed_levels.append('student')
        if current_rank >= 2: allowed_levels.append('associate')
        if current_rank >= 3: allowed_levels.append('full')
        if current_rank >= 4: allowed_levels.append('fellow')
        
        resources = Resource.objects.filter(access_level__in=allowed_levels)

    category_filter = request.GET.get('cat')
    if category_filter:
        resources = resources.filter(category=category_filter)

    return render(request, 'accounts/resources.html', {'resources': resources})

@login_required
def member_id(request):
    """
    This view generates the Digital ID Card.
    It ensures the context variables 'member' and 'student_info' match the template logic.
    """
    # 1. Fetch the student profile if it exists
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    
    # 2. Safety check: If they are a student but haven't filled their school info
    if request.user.membership_tier == 'student' and not student_profile:
        # Note: 'profile' should be the name of your profile URL in urls.py
        messages.error(request, "Action Required: Please complete your Student Academic Details to view your ID Card.")
        return redirect('profile')

    # 3. Context names MUST match the template (member_id.html) exactly.
    # We use 'member' instead of 'user' to avoid conflicts with Django's global user context.
    context = {
        'member': request.user,
        'student_info': student_profile,
        'expiry_date': 'December 2026'
    }
    
    return render(request, 'accounts/member_id.html', context)


@login_required
def student_hub(request):
    
    if request.user.membership_tier != 'student':
        messages.warning(request, "This section is for Student Members only.")
        return redirect('profile')

    student_profile = StudentProfile.objects.filter(user=request.user).first()
    if not student_profile:
        messages.error(request, "Action Required: Please complete your Student Details to access the Student Hub.")
        return redirect('profile')

    resources = Resource.objects.filter(category='academic')

    # 4. Apply Verification and Access Level rules
    if not request.user.is_verified:
        resources = resources.filter(access_level='public')
    else:
        resources = resources.filter(access_level__in=['public', 'student'])

    if not request.user.is_verified:
        resources = resources.filter(is_verified_only=False)

    resources = resources.order_by('-uploaded_at')[:4]

    announcements = StudentAnnouncement.objects.all().order_by('-date_posted')
    announcements = announcements.filter(
        target_university__in=['All', student_profile.university]
    )

    return render(request, 'accounts/student_hub.html', {
        'announcements': announcements,
        'resources': resources,  # Now the template can see the files!
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
    
@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

def announcement(request, pk):
    announcement = get_object_or_404(
        Announcement,
        pk=pk,
        is_published=True
    )

    return render(
        request,
        'accounts/announcement.html',
        {'announcement': announcement}
    )

class MemberListAPI(APIView):
    def get(self, request):
        members = User.objects.all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

@login_required
def exco_master_dashboard(request):
    # Security: Only allow users with the 'EXCO' role
    is_exco = request.user.roles.filter(name="EXCO").exists()
    is_trustee = request.user.roles.filter(name="Trustee").exists()

    if not (is_exco or is_trustee):
        messages.error(request, "Access restricted to Academy Leadership.")
        return redirect('profile')

    # 1. Gather Academy-wide Metrics
    
    total_members = User.objects.count()
    verified_members = User.objects.filter(is_verified=True).count()
    
    # Filter out staff/admins from pending counts to keep it focused on members
    pending_members_queryset = User.objects.filter(is_verified=False, is_staff=False)
    pending_verifications = pending_members_queryset.count()
    
    # 2. Committee Oversight
    committees = Committee.objects.all()
    latest_reports = CommitteeReport.objects.all().order_by('-uploaded_at')[:10]

    context = {
        'total_members': total_members,
        'is_trustee': is_trustee,
        'verified_members': verified_members,
        'pending_count': pending_verifications,
        'pending_members': pending_members_queryset, # <-- COMMA REMOVED HERE
        'committees': committees,
        'latest_reports': latest_reports,
    }
    return render(request, 'accounts/exco_master_dashboard.html', context)

@login_required
def exco_verify_member(request, user_id):
    # Security: Ensure ONLY EXCO can do this
    if not request.user.roles.filter(name="EXCO").exists():
        messages.error(request, "Unauthorized access.")
        return redirect('profile')
        
    member_to_verify = get_object_or_404(User, id=user_id)
    member_to_verify.is_verified = True
    member_to_verify.save() # This triggers the SendGrid email automatically
    
    messages.success(request, f"Member {member_to_verify.username} is now verified.")
    return redirect('exco_master_dashboard')

@login_required
def post_national_announcement(request):
    if not request.user.roles.filter(name="EXCO").exists():
        return redirect('profile')

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            # Create a general announcement for the Home Page
            Announcement.objects.create(title=title, content=content)
            messages.success(request, "National announcement published!")
        else:
            messages.error(request, "Title and Content are required.")
            
    return redirect('exco_master_dashboard')


@login_required
def committee_dashboard(request, pk):
    # Use the pk from the URL to get the specific committee
    committee = get_object_or_404(Committee, pk=pk)
    
    # Security: Ensure the user is the Director of THIS committee or EXCO
    is_exco = request.user.roles.filter(name__in=["Exco", "Trustee"]).exists()
    if committee.director != request.user and not is_exco:
        messages.warning(request, "Access Denied: You do not manage this committee.")
        return redirect('profile')

    ann_form = CommitteeAnnouncementForm()
    report_form = CommitteeReportForm()

    if request.method == 'POST':
        if 'post_announcement' in request.POST:
            ann_form = CommitteeAnnouncementForm(request.POST)
            if ann_form.is_valid():
                ann = ann_form.save(commit=False)
                ann.committee = committee
                ann.author = request.user
                ann.save()
                messages.success(request, "Announcement posted!")
                # FIX: Pass the pk back to the redirect
                return redirect('committee_dashboard', pk=pk)

        elif 'upload_report' in request.POST:
            report_form = CommitteeReportForm(request.POST, request.FILES)
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.committee = committee
                report.submitted_by = request.user
                report.save()
                messages.success(request, "Report uploaded!")
                # FIX: Pass the pk back to the redirect
                return redirect('committee_dashboard', pk=pk)

    context = {
        'committee': committee,
        'members': committee.members.all(),
        'member_count': committee.members.count(),
        'announcements': committee.announcements.all().order_by('-date_posted'),
        'reports': committee.reports.all().order_by('-uploaded_at'),
        'ann_form': ann_form,
        'report_form': report_form,
    }
    return render(request, 'accounts/committee_dashboard.html', context)

class ExcoReportFetchAPI(APIView):
    def get(self, request):
        # Security Check: Does this user have the 'EXCO' role?
        if not request.user.roles.filter(name="EXCO").exists():
            return Response({"error": "Unauthorized"}, status=403)
        
        reports = CommitteeReport.objects.all().order_by('-uploaded_at')
        serializer = CommitteeReportSerializer(reports, many=True)
        return Response(serializer.data)
    
@login_required
def submit_article(request):
    if not request.user.is_verified:
        messages.warning(request, "Only verified members can submit articles for the NAA Journal.")
        return redirect('profile')

    if request.method == 'POST':
        form = ArticleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = 'draft' # Force draft status for review
            article.save()
            
            send_mail(
                subject="New NAA Article Submitted for Review",
                message=f"A new article titled '{article.title}' has been submitted by {request.user.username}. Please log in to the EXCO Dashboard to review it.",
                from_email="nigerianacademyofaudiology@gmail.com",
                recipient_list=["nigerianacademyofaudiology@gmail.com"], # Or your specific EXCO list
                fail_silently=True,
            )

            messages.success(request, "Article submitted! It will be live after committee review.")
            return redirect('profile')
    else:
        form = ArticleSubmissionForm()

    return render(request, 'accounts/submit_article.html', {'form': form})

def article_detail(request, pk):
    # This specifically looks for an Article, not an Announcement
    article = get_object_or_404(Article, pk=pk, status='published')
    return render(request, 'accounts/article_detail.html', {'article': article})

@login_required
def export_members_csv(request, committee_id=None):  # Add =None here
    is_exco_trustee = request.user.roles.filter(name__in=["Exco", "Trustee"]).exists()
    
    # 1. Logic for Committee Export
    if committee_id:
        committee = get_object_or_404(Committee, id=committee_id)
        is_director = (committee.director == request.user)
        
        if not (is_exco_trustee or is_director):
            messages.error(request, "Access restricted.")
            return redirect('profile')
            
        members = committee.members.all()
        filename = f"{committee.name}_Members.csv"
        
    # 2. Logic for Full Academy Export (EXCO/Trustee only)
    else:
        if not is_exco_trustee:
            messages.error(request, "Access restricted to EXCO.")
            return redirect('profile')
            
        members = User.objects.all()
        filename = "NAA_Full_Member_List.csv"

    # 3. Apply Filters
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    if start_date:
        members = members.filter(date_joined__date__gte=start_date)
    if end_date:
        members = members.filter(date_joined__date__lte=end_date)

    # 4. Generate Response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Tier', 'Date Joined'])

    for m in members:
        writer.writerow([m.username, m.email, m.get_membership_tier_display(), m.date_joined])

    return response

@login_required
def committee_workspace(request, pk):
    committee = get_object_or_404(Committee, pk=pk)
    
    # Check if the user is actually a member of this committee
    is_member = committee.members.filter(id=request.user.id).exists()
    is_director = (committee.director == request.user)
    is_exco = request.user.roles.filter(name__in=["Exco", "Trustee"]).exists()

    if not (is_member or is_director or is_exco):
        messages.error(request, "You are not assigned to this committee.")
        return redirect('profile')

    context = {
        'committee': committee,
        'members': committee.members.all(),
        'reports': committee.reports.all(), # Reports shared with the team
        'announcements': announcements,
        'is_director': is_director,
        'is_exco': is_exco,
    }
    return render(request, 'accounts/committee_workspace.html', context)

@login_required
def delete_committee_announcement(request, pk):
    announcement = get_object_or_404(CommitteeAnnouncement, pk=pk)
    committee_id = announcement.committee.id
    
    # Security: Only the Director of the committee or EXCO can delete
    is_exco = request.user.roles.filter(name__in=["Exco", "Trustee"]).exists()
    if announcement.committee.director != request.user and not is_exco:
        messages.error(request, "Unauthorized to delete this announcement.")
        return redirect('committee_dashboard', pk=committee_id)

    announcement.delete()
    messages.success(request, "Announcement removed.")
    return redirect('committee_dashboard', pk=committee_id)

@login_required
def delete_committee_report(request, pk):
    report = get_object_or_404(CommitteeReport, pk=pk)
    committee_id = report.committee.id
    
    # Security check
    is_exco = request.user.roles.filter(name__in=["Exco", "Trustee"]).exists()
    if report.committee.director != request.user and not is_exco:
        messages.error(request, "Unauthorized to delete this report.")
        return redirect('committee_dashboard', pk=committee_id)

    report.delete()
    messages.success(request, "Report deleted.")
    return redirect('committee_dashboard', pk=committee_id)