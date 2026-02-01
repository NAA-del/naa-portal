import os
import csv
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from collections import defaultdict

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAuthenticated

# Local imports
from .decorators import (
    committee_director_required,
    committee_member_required,
    exco_required,
    verified_member_required,
)
from .models import (
    User,
    AboutPage,
    Announcement,
    Executive,
    Resource,
    StudentProfile,
    StudentAnnouncement,
    CPDRecord,
    Notification,
    Article,
    Committee,
    CommitteeReport,
    CommitteeAnnouncement,
    send_verification_email,
)
from .forms import (
    NAAUserCreationForm,
    StudentProfileForm,
    ProfilePictureForm,
    CPDSubmissionForm,
    CommitteeReportForm,
    CommitteeAnnouncementForm,
    ArticleSubmissionForm,
    UserUpdateForm,
    ContactForm,
)
from .serializers import MemberSerializer, CommitteeReportSerializer

# Configure logging
logger = logging.getLogger("accounts")


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================


@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def login_view(request):
    """
    User login with rate limiting (max 5 attempts per minute).
    """
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                logger.info(f"User {username} logged in successfully")
                messages.success(request, f"Welcome back, {username}!")

                # Redirect to next page or home
                redirect_url = request.GET.get("next", "home")
                return redirect(redirect_url)
            else:
                logger.warning(f"Failed login attempt for username: {username}")
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


@ratelimit(key='ip', rate='10/h', method='POST', block=True)
def register(request):
    """
    User registration with rate limiting (max 10 registrations per hour).
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = NAAUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            
            login(request, user)
            
            logger.info(f"New user registered: {user.username} ({user.email})")
            
            messages.success(
                request,
                "Registration successful! Welcome to NAA. "
                "Your account is pending verification by admin."
            )
            
            if user.membership_tier == 'student':
                messages.info(request, "Please complete your student profile.")
                return redirect('profile')
            
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = NAAUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """User logout"""
    username = request.user.username if request.user.is_authenticated else "User"
    logout(request)
    logger.info(f"{username} logged out")
    messages.info(request, "You have been logged out.")
    return redirect("home")


# ============================================================================
# PUBLIC VIEWS
# ============================================================================


def home(request):
    """
    Homepage with announcements, articles, and executive leadership.
    Implements caching and pagination for performance.
    """
    # Get announcements with pagination
    announcements_list = (
        Announcement.objects.filter(is_published=True)
        .select_related("author")
        .order_by("-featured", "-date_posted")
    )

    # Paginate announcements
    paginator = Paginator(announcements_list, 12)
    page_number = request.GET.get("page", 1)

    try:
        announcements = paginator.page(page_number)
    except PageNotAnInteger:
        announcements = paginator.page(1)
    except EmptyPage:
        announcements = paginator.page(paginator.num_pages)

    # Get recent articles
    articles = (
        Article.objects.filter(status="published", is_public=True)
        .select_related("author")
        .order_by("-created_at")[:3]
    )
    
    # Cache executives (they rarely change)
    executives = cache.get("naa_executives")
    if not executives:
        executives = (
            Executive.objects.filter(is_active=True)
            .select_related("user")
            .order_by("rank")[:8]
        )
        cache.set("naa_executives", executives, 3600)  # Cache for 1 hour

    return render(
        request,
        "accounts/home.html",
        {
            "announcements": announcements,
            "articles": articles,
            "executives": executives,
        },
    )


def about(request):
    """About page with academy information"""
    about_info = AboutPage.objects.first()

    if not about_info:
        # Provide default content if none exists
        about_info = {
            "title": "About the Academy",
            "history_text": "History content pending...",
            "mission": "Mission statement pending...",
            "vision": "Vision statement pending...",
            "aims_and_objectives": "Objectives pending...",
        }

    return render(request, "accounts/about.html", {"about": about_info})


def announcement(request, pk):
    """View single announcement detail"""
    announcement = get_object_or_404(Announcement, pk=pk, is_published=True)
    return render(request, "accounts/announcement.html", {"announcement": announcement})


def article_detail(request, pk):
    """View single article detail"""
    article = get_object_or_404(Article, pk=pk, status="published")
    return render(request, "accounts/article_detail.html", {"article": article})



def contact_us(request):
    """Public contact form for general inquiries."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            phone_number = form.cleaned_data.get('phone_number', 'N/A')

            full_message = f"Name: {name}\nEmail: {email}\nPhone: {phone_number}\n\nMessage:\n{message}"

            try:
                send_mail(
                    subject=f"NAA Contact Form: {subject}",
                    message=full_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL], # Send to admin email
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
                return redirect('contact')
            except Exception as e:
                logger.error(f"Contact form email send error: {e}")
                messages.error(request, 'There was an error sending your message. Please try again later.')
    else:
        form = ContactForm()

    return render(request, 'accounts/contact.html', {'form': form})

# ============================================================================
# AUTHENTICATED USER VIEWS
# ============================================================================


@login_required
def profile(request):
    """User profile page with multiple forms"""
    
    # Initialize all forms first
    p_form = ProfilePictureForm(instance=request.user)
    u_form = UserUpdateForm(instance=request.user)
    
    # Handle Profile Picture Update
    if request.method == 'POST' and 'profile_picture' in request.FILES:
        p_form = ProfilePictureForm(request.POST, request.FILES, instance=request.user)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Profile picture updated!")
            return redirect('profile')
    
    # Handle Name Update
    elif request.method == 'POST' and 'update_info' in request.POST:
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, "Name updated successfully!")
            return redirect('profile')
    
    # Handle Student Profile
    student_profile = StudentProfile.objects.filter(user=request.user).first()
    s_form = None
    
    if request.user.membership_tier == 'student':
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
    
    context = {
        'user': request.user,
        'p_form': p_form,
        'u_form': u_form,
        's_form': s_form,
        'student_profile': student_profile,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def download_constitution(request):
    """
    Secure download of NAA constitution (verified members only).
    Implements path traversal protection.
    """
    if not request.user.is_verified:
        messages.warning(
            request, "Only verified members can download the constitution."
        )
        return redirect("profile")

    # Define allowed files (whitelist approach)
    ALLOWED_FILES = {
        "constitution": "constitution.pdf",
        "bylaws": "bylaws.pdf",
    }

    # Get requested file
    file_key = request.GET.get("doc", "constitution")

    if file_key not in ALLOWED_FILES:
        raise Http404("Document not found")

    filename = ALLOWED_FILES[file_key]

    # Construct safe file path
    file_path = os.path.join(settings.BASE_DIR, "static", "docs", filename)

    # Verify path is within allowed directory (prevent path traversal)
    allowed_dir = os.path.join(settings.BASE_DIR, "static", "docs")
    real_path = os.path.realpath(file_path)

    if not real_path.startswith(os.path.realpath(allowed_dir)):
        logger.warning(f"Path traversal attempt by {request.user.username}")
        raise Http404("Access denied")

    if not os.path.exists(file_path):
        messages.error(request, "Constitution file is currently unavailable.")
        return redirect("home")

    logger.info(f"{request.user.username} downloaded {filename}")
    return FileResponse(
        open(file_path, "rb"), as_attachment=True, filename=f"NAA_{filename}"
    )


@login_required
@verified_member_required
def member_id(request):
    """Digital membership ID card (verified members only)"""
    return render(request, "accounts/member_id.html")


@login_required
def mark_notification_read(request, pk):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect("profile")


# ============================================================================
# RESOURCE & CPD VIEWS
# ============================================================================


@login_required
def resource_library(request):
    """
    Resource library with tier-based access control.
    """
    user = request.user

    # Define tier hierarchy
    tier_rank = {"student": 1, "associate": 2, "full": 3, "fellow": 4}

    current_rank = tier_rank.get(user.membership_tier, 0)

    # Build allowed access levels
    allowed_levels = ["public"]
    if current_rank >= 1:
        allowed_levels.append("student")
    if current_rank >= 2:
        allowed_levels.append("associate")
    if current_rank >= 3:
        allowed_levels.append("full")
    if current_rank >= 4:
        allowed_levels.append("fellow")

    # Fetch resources within allowed levels
    resources = (
        Resource.objects.filter(access_level__in=allowed_levels)
        .select_related("uploaded_by")
        .only("id", "title", "category", "file", "description", "uploaded_at", "uploaded_by")
    )

    # Restrict to verified members if required
    if not user.is_verified:
        resources = resources.filter(is_verified_only=False)

    # Group by category
    categorized = defaultdict(list)
    for resource in resources:
        categorized[resource.get_category_display()].append(resource)

    return render(
        request,
        "accounts/resources.html",
        {
            "categorized_resources": dict(categorized),
        },
    )


@login_required
@verified_member_required
def cpd_tracker(request):
    """
    CPD tracking system for full members and fellows.
    """
    # Only full members and fellows need CPD
    if request.user.membership_tier not in ["full", "fellow"]:
        messages.warning(request, "CPD tracking is for Full Members and Fellows only.")
        return redirect("profile")

    # Get user's CPD records
    cpd_records = CPDRecord.objects.filter(user=request.user).order_by(
        "-date_completed"
    )

    # Calculate statistics efficiently
    stats = cpd_records.aggregate(
        total_points=Sum("points"),
        verified_points=Sum("points", filter=Q(is_verified=True)),
        total_activities=Count("id"),
        verified_activities=Count("id", filter=Q(is_verified=True)),
    )

    # Handle CPD submission
    if request.method == "POST":
        form = CPDSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            cpd = form.save(commit=False)
            cpd.user = request.user
            cpd.save()

            logger.info(
                f"CPD record created by {request.user.username}: {cpd.activity_name}"
            )
            messages.success(request, "CPD activity submitted for review!")
            return redirect("cpd_tracker")
    else:
        form = CPDSubmissionForm()

    context = {
        "records": cpd_records,
        "form": form,
        "total_points": stats["total_points"] or 0,
        "verified_points": stats["verified_points"] or 0,
        "total_activities": stats["total_activities"],
        "verified_activities": stats["verified_activities"],
    }

    return render(request, "accounts/cpd_tracker.html", context)


# ============================================================================
# STUDENT HUB
# ============================================================================


@login_required
def student_hub(request):
    """
    Student-only hub with targeted announcements and resources.
    """
    # Security: Only students can access
    if request.user.membership_tier != "student":
        messages.warning(request, "This page is only for student members.")
        return redirect("profile")

    # Get or create student profile
    try:
        student_profile = request.user.student_info
    except StudentProfile.DoesNotExist:
        messages.info(request, "Please complete your student profile first.")
        return redirect("profile")

    # Get student announcements (all universities + user's university)
    student_announcements = (
        StudentAnnouncement.objects.filter(
            Q(target_university="All")
            | Q(target_university=student_profile.university),
            is_published=True,
        )
        .select_related("author")
        .order_by("-date_posted")[:5]
    )

    # Get university statistics
    stats = (
        StudentProfile.objects.values("university")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # Get student resources
    resources = (
        Resource.objects.filter(
            category="academic", access_level__in=["public", "student"]
        )
        .select_related("uploaded_by")
        .order_by("-uploaded_at")[:8]
    )

    context = {
        "student_announcements": student_announcements,
        "stats": stats,
        "resources": resources,
    }

    return render(request, "accounts/student_hub.html", context)


# ============================================================================
# COMMITTEE VIEWS
# ============================================================================


@login_required
@committee_director_required
def committee_dashboard(request, pk):
    """
    Committee management dashboard (directors only).
    Handles announcements, reports, and member management.
    """
    committee = get_object_or_404(Committee, pk=pk)

    ann_form = CommitteeAnnouncementForm()
    report_form = CommitteeReportForm()

    if request.method == "POST":
        # Handle announcement posting
        if "post_announcement" in request.POST:
            ann_form = CommitteeAnnouncementForm(request.POST)
            if ann_form.is_valid():
                ann = ann_form.save(commit=False)
                ann.committee = committee
                ann.author = request.user
                ann.save()

                logger.info(
                    f"{request.user.username} posted announcement in {committee.name}"
                )
                messages.success(request, "Announcement posted!")
                return redirect("committee_dashboard", pk=pk)

        # Handle report upload
        elif "upload_report" in request.POST:
            report_form = CommitteeReportForm(request.POST, request.FILES)
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.committee = committee
                report.submitted_by = request.user
                report.save()

                logger.info(
                    f"{request.user.username} uploaded report to {committee.name}"
                )
                messages.success(request, "Report uploaded!")
                return redirect("committee_dashboard", pk=pk)

    context = {
        "committee": committee,
        "members": committee.members.select_related("student_info").all(),
        "member_count": committee.members.count(),
        "announcements": committee.announcements.select_related("author").order_by(
            "-date_posted"
        )[:10],
        "reports": committee.reports.select_related("submitted_by").order_by(
            "-uploaded_at"
        )[:20],
        "ann_form": ann_form,
        "report_form": report_form,
    }

    return render(request, "accounts/committee_dashboard.html", context)


@login_required
@committee_member_required
def committee_workspace(request, pk):
    """
    Committee workspace for members to view announcements and reports.
    """
    committee = get_object_or_404(Committee, pk=pk)

    is_director = committee.director == request.user
    is_exco = request.user.is_exco_or_trustee()

    context = {
        "committee": committee,
        "members": committee.members.select_related("student_info").all(),
        "reports": committee.reports.select_related("submitted_by").order_by(
            "-uploaded_at"
        )[:20],
        "announcements": committee.announcements.select_related("author").order_by(
            "-date_posted"
        )[:10],
        "is_director": is_director,
        "is_exco": is_exco,
    }

    return render(request, "accounts/committee_workspace.html", context)


@login_required
def delete_committee_announcement(request, pk):
    """Delete committee announcement (director/EXCO only)"""
    announcement = get_object_or_404(CommitteeAnnouncement, pk=pk)
    committee_id = announcement.committee.id

    # Security check
    is_director = announcement.committee.director == request.user
    is_exco = request.user.is_exco_or_trustee()

    if not (is_director or is_exco):
        logger.warning(
            f"Unauthorized delete attempt by {request.user.username} "
            f"on announcement {pk}"
        )
        raise PermissionDenied("You don't have permission to delete this.")

    logger.info(
        f"{request.user.username} deleted announcement '{announcement.title}' "
        f"from {announcement.committee.name}"
    )

    announcement.delete()
    messages.success(request, "Announcement deleted.")

    return redirect("committee_dashboard", pk=committee_id)


@login_required
def delete_committee_report(request, pk):
    """Delete committee report (director/EXCO only)"""
    report = get_object_or_404(CommitteeReport, pk=pk)
    committee_id = report.committee.id

    # Security check
    is_director = report.committee.director == request.user
    is_exco = request.user.is_exco_or_trustee()

    if not (is_director or is_exco):
        logger.warning(
            f"Unauthorized delete attempt by {request.user.username} " f"on report {pk}"
        )
        raise PermissionDenied("You don't have permission to delete this.")

    logger.info(
        f"{request.user.username} deleted report '{report.title}' "
        f"from {report.committee.name}"
    )

    report.delete()
    messages.success(request, "Report deleted.")

    return redirect("committee_dashboard", pk=committee_id)


# ============================================================================
# EXCO VIEWS
# ============================================================================


@login_required
@exco_required
def exco_master_dashboard(request):
    """
    Executive command center with academy-wide statistics and controls.
    """
    # Get statistics
    total_members = User.objects.count()
    verified_members = User.objects.filter(is_verified=True).count()
    pending_count = User.objects.filter(is_verified=False, is_staff=False).count()

    # Get committees
    committees = Committee.objects.prefetch_related("members").all()

    # Get latest reports
    latest_reports = CommitteeReport.objects.select_related(
        "committee", "submitted_by"
    ).order_by("-uploaded_at")[:10]

    # Get pending members
    pending_members = User.objects.filter(is_verified=False, is_staff=False).order_by(
        "-date_joined"
    )[:20]

    # Check if user is trustee
    is_trustee = request.user.has_role("trustee")

    context = {
        "total_members": total_members,
        "verified_members": verified_members,
        "pending_count": pending_count,
        "committees": committees,
        "latest_reports": latest_reports,
        "pending_members": pending_members,
        "is_trustee": is_trustee,
    }

    return render(request, "accounts/exco_master_dashboard.html", context)


@login_required
@exco_required
def exco_verify_member(request, user_id):
    """Verify a member (EXCO only)"""
    member = get_object_or_404(User, id=user_id)

    if member.is_verified:
        messages.info(request, f"{member.username} is already verified.")
    else:
        member.is_verified = True
        member.date_verified = timezone.now()
        member.save()

        # Send verification email
        send_verification_email(member)

        logger.info(f"{request.user.username} verified member {member.username}")
        messages.success(request, f"{member.username} has been verified!")

    return redirect("exco_master_dashboard")


@login_required
@exco_required
def post_national_announcement(request):
    """Post national announcement (EXCO only)"""
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()

        if title and content:
            announcement = Announcement.objects.create(
                title=title, content=content, author=request.user
            )

            logger.info(
                f"{request.user.username} posted national announcement: {title}"
            )
            messages.success(request, "National announcement published!")
        else:
            messages.error(request, "Title and content are required.")

    return redirect("exco_master_dashboard")


@login_required
def export_members_csv(request, committee_id=None):
    """
    Export members to CSV.
    If committee_id provided, exports that committee's members.
    Otherwise, exports all members (EXCO only).
    """
    is_exco_trustee = request.user.is_exco_or_trustee()

    # Committee export
    if committee_id:
        committee = get_object_or_404(Committee, id=committee_id)
        is_director = committee.director == request.user

        if not (is_exco_trustee or is_director):
            messages.error(request, "Access restricted.")
            return redirect("profile")

        members = committee.members.all()
        filename = f"{committee.name}_Members.csv"

    # Full academy export (EXCO only)
    else:
        if not is_exco_trustee:
            messages.error(request, "Access restricted to EXCO.")
            return redirect("profile")

        members = User.objects.all()
        filename = "NAA_Full_Member_List.csv"

    # Apply date filters
    start_date = request.GET.get("start")
    end_date = request.GET.get("end")

    if start_date:
        members = members.filter(date_joined__date__gte=start_date)
    if end_date:
        members = members.filter(date_joined__date__lte=end_date)

    # Generate CSV response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["Username", "Email", "Tier", "Verified", "Date Joined"])

    # Stream results for memory efficiency
    for m in members.iterator(chunk_size=1000):
        writer.writerow(
            [
                m.username,
                m.email,
                m.get_membership_tier_display(),
                "Yes" if m.is_verified else "No",
                m.date_joined.strftime("%Y-%m-%d"),
            ]
        )

    logger.info(f"{request.user.username} exported CSV: {filename}")
    return response


# ============================================================================
# ARTICLE VIEWS
# ============================================================================


@login_required
@verified_member_required
def submit_article(request):
    """Submit article for journal (verified members only)"""
    if request.method == "POST":
        form = ArticleSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.status = "draft"  # Requires EXCO review
            article.save()

            # Notify EXCO
            try:
                send_mail(
                    subject="New NAA Article Submitted for Review",
                    message=f"Article '{article.title}' submitted by {request.user.username}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send article notification: {e}")

            logger.info(f"{request.user.username} submitted article: {article.title}")
            messages.success(request, "Article submitted for review!")
            return redirect("profile")
    else:
        form = ArticleSubmissionForm()

    return render(request, "accounts/submit_article.html", {"form": form})


# ============================================================================
# API VIEWS
# ============================================================================


class MemberListAPI(APIView):
    """
    API endpoint for member listing (authenticated users only).
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        """Get list of verified members"""
        # Only verified members can access
        if not request.user.is_verified:
            return Response(
                {"error": "Only verified members can access this API."}, status=403
            )

        # Don't expose sensitive data
        members = User.objects.filter(is_verified=True).values(
            "id", "username", "membership_tier"
        )

        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)


class ExcoReportFetchAPI(APIView):
    """
    API endpoint for fetching committee reports (EXCO only).
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        """Get all committee reports"""
        # Security: Only EXCO can access
        if not request.user.is_exco_or_trustee():
            return Response(
                {"error": "Unauthorized. EXCO access required."}, status=403
            )

        reports = CommitteeReport.objects.select_related(
            "committee", "submitted_by"
        ).order_by("-uploaded_at")[:50]

        serializer = CommitteeReportSerializer(reports, many=True)
        return Response(serializer.data)

# ============================================================================
# RATE LIMIT HANDLER
# ============================================================================

def rate_limited(request, exception):
    """Custom handler for rate-limited requests"""
    return HttpResponse(
        "You've made too many registration attempts. "
        "Please try again in an hour.",
        status=429
    )