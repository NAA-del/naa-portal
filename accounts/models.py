from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging
import re

logger = logging.getLogger('accounts')

# ============================================================================
# ROLE & COMMITTEE MODELS
# ============================================================================

class Role(models.Model):
    
    name = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Type the role name here (e.g., Student Member, Executive)"
    )

    permissions_level = models.IntegerField(
        default=1,
        help_text="Higher number = more authority (1-10)"
    )

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-permissions_level']
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'


class Committee(models.Model):
    """
    Organizational committees with directors and members.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Committee name (e.g., SCOPHA, Education Committee)"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of committee purpose"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='committees',
        blank=True
    )
    director = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='directed_committees',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Committee'
        verbose_name_plural = 'Committees'


# ============================================================================
# USER MODEL
# ============================================================================

class User(AbstractUser):
    """
    Custom user model for NAA Portal with membership tiers and roles.
    """
    
    TIER_CHOICES = [
        ('student', 'Student Member'),
        ('associate', 'Associate Member'),
        ('full', 'Full Member'),
        ('fellow', 'Fellow'),
    ]
    
    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?234?\d{10}$',
        message="Phone number must be in format: '+2348012345678' or '08012345678'"
    )
    
    # Profile fields
    profile_picture = CloudinaryField(
        'image',
        null=True,
        blank=True,
        folder='profile_pictures'
    )
    membership_tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default='student',
        db_index=True
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[phone_regex],
        help_text="Nigerian phone number"
    )
    
    # Verification fields
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Admin-verified member status"
    )
    date_verified = models.DateTimeField(
        null=True,
        blank=True,
        editable=False
    )
    
    # Role assignment
    roles = models.ManyToManyField(
        Role,
        blank=True,
        related_name='users'
    )
    
    def has_role(self, *role_names):
        """
        Check if user has any of the specified roles.
        
        Args:
            *role_names: Variable number of role names (lowercase)
        
        Returns:
            bool: True if user has at least one of the roles
        
        Example:
            user.has_role('exco', 'trustee')
        """
        normalized_roles = [r.lower() for r in role_names]
        return self.roles.filter(name__in=normalized_roles).exists()
    
    def is_exco_or_trustee(self):
        """Quick check if user is leadership (EXCO or Trustee)"""
        return self.has_role('exco', 'trustee')
    
    def is_committee_director_of(self, committee):
        """Check if user is director of a specific committee"""
        return committee.director == self
    
    def get_display_name(self):
        """Get user's display name (full name or username)"""
        return self.get_full_name() or self.username
    
    def clean(self):
        """
        Model-level validation.
        Note: This is called by forms, not automatically on save.
        """
        super().clean()
        
        # Email uniqueness (case-insensitive)
        if self.email:
            existing = User.objects.filter(
                email__iexact=self.email
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError({
                    'email': 'This email address is already registered.'
                })
        
        # Username format validation
        if not re.match(r'^[a-zA-Z0-9_]+$', self.username):
            raise ValidationError({
                'username': 'Username can only contain letters, numbers, and underscores.'
            })
    
    def save(self, *args, **kwargs):
        """
        Override save to normalize data before saving.
        """
        # Normalize email to lowercase
        if self.email:
            self.email = self.email.lower().strip()
        
        # Normalize phone number
        if self.phone_number:
            self.phone_number = self.phone_number.replace(' ', '').replace('-', '')
        
        # Set verification date when verified
        if self.is_verified and not self.date_verified:
            self.date_verified = timezone.now()
        
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'NAA Member'
        verbose_name_plural = 'NAA Members'
        indexes = [
            models.Index(fields=['membership_tier', 'is_verified']),
            models.Index(fields=['email']),
            models.Index(fields=['-date_joined']),
        ]


# ============================================================================
# EXECUTIVE LEADERSHIP MODEL
# ============================================================================

class Executive(models.Model):
    """
    Executive leadership profiles displayed on homepage.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='executive_profile'
    )
    position = models.CharField(
        max_length=100,
        help_text="e.g., National President, Vice President"
    )
    bio = models.TextField(
        blank=True,
        help_text="Short bio displayed on homepage"
    )
    rank = models.PositiveIntegerField(
        default=1,
        help_text="Display order (1 for President, 2 for VP, etc.)"
    )
    term_start_date = models.DateField()
    term_end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Active executives shown on homepage"
    )

    def __str__(self):
        return f"{self.position} - {self.user.get_display_name()}"
    
    class Meta:
        ordering = ['rank']
        verbose_name = 'Executive Officer'
        verbose_name_plural = 'Executive Officers'


# ============================================================================
# STUDENT PROFILE MODEL
# ============================================================================

class StudentProfile(models.Model):
    """
    Additional profile information for student members.
    """
    
    UNIVERSITY_CHOICES = [
        ('UNIMED', 'University of Medical Sciences, Ondo (UNIMED)'),
        ('FUHSI', 'Federal University of Health Sciences, Ila-Orangun (FUHSI)'),
        ('FUHSA', 'Federal University of Health Sciences, Azare (FUHSA)'),
        ('FUDMA', 'Federal University Dutsin-Ma, Katsina (FUDMA)'),
    ]
    
    LEVEL_CHOICES = [
        (100, '100 Level'),
        (200, '200 Level'),
        (300, '300 Level'),
        (400, '400 Level'),
        (500, '500 Level'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_info'
    )
    university = models.CharField(
        max_length=100,
        choices=UNIVERSITY_CHOICES,
        db_index=True,
        help_text="Select your university"
    )
    matric_number = models.CharField(
        max_length=30,
        unique=True,
        help_text="University matriculation number"
    )
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        help_text="Current academic level"
    )
    
    def clean(self):
        """Validate student profile data"""
        super().clean()
        
        # Normalize and validate matric number
        if self.matric_number:
            self.matric_number = self.matric_number.replace(' ', '').upper()
            
            if not re.match(r'^[A-Z0-9/]{5,30}$', self.matric_number):
                raise ValidationError({
                    'matric_number': 'Invalid format. Use letters, numbers, and slashes only.'
                })
        
        # Verify user is a student (only if user is already set)
        if self.user_id:
            try:
                user = User.objects.get(pk=self.user_id)
                if user.membership_tier != 'student':
                    raise ValidationError({
                        'user': 'Only student members can have a student profile.'
                    })
            except User.DoesNotExist:
                pass
    
    def save(self, *args, **kwargs):
        """Validate before saving"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_university_display()})"
    
    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'
        indexes = [
            models.Index(fields=['university']),
        ]


# ============================================================================
# ANNOUNCEMENT BASE CLASS
# ============================================================================

class BaseAnnouncement(models.Model):
    """
    Abstract base class for all announcement types.
    Ensures consistency across national, student, and committee announcements.
    """
    title = models.CharField(max_length=255)
    summary = models.TextField(
        blank=True,
        help_text="Short preview shown in listings"
    )
    content = CKEditor5Field(config_name='default')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Who created this announcement"
    )
    image = CloudinaryField(
        'image',
        blank=True,
        null=True,
        folder='announcements'
    )
    
    # Status fields
    is_published = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Uncheck to hide this announcement"
    )
    featured = models.BooleanField(
        default=False,
        help_text="Featured announcements appear first"
    )
    
    # Timestamps
    date_posted = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-featured', '-date_posted']
    
    def __str__(self):
        return self.title


class Announcement(BaseAnnouncement):
    """National announcements visible to all members on homepage"""
    
    class Meta:
        verbose_name = 'National Announcement'
        verbose_name_plural = 'National Announcements'
        ordering = ['-featured', '-date_posted']
        indexes = [
            models.Index(fields=['-date_posted', 'is_published']),
            models.Index(fields=['featured', '-date_posted']),
        ]


class StudentAnnouncement(BaseAnnouncement):
    """Announcements targeted to student members"""
    
    UNIVERSITY_CHOICES = [
        ('All', 'All Universities'),
        ('UNIMED', 'University of Medical Sciences, Ondo'),
        ('FUHSI', 'Federal University of Health Sciences, Ila-Orangun'),
        ('FUHSA', 'Federal University of Health Sciences, Azare'),
        ('FUDMA', 'Federal University Dutsin-Ma, Katsina'),
    ]
    
    target_university = models.CharField(
        max_length=20,
        choices=UNIVERSITY_CHOICES,
        default='All',
        db_index=True,
        help_text="Target specific university or all"
    )
    
    class Meta:
        verbose_name = 'Student Announcement'
        verbose_name_plural = 'Student Announcements'
        ordering = ['-date_posted']
        indexes = [
            models.Index(fields=['target_university', '-date_posted']),
            models.Index(fields=['is_published', '-date_posted']),
        ]


class CommitteeAnnouncement(BaseAnnouncement):
    """Announcements for specific committees"""
    
    committee = models.ForeignKey(
        Committee,
        on_delete=models.CASCADE,
        related_name='announcements',
        help_text="Which committee this announcement is for"
    )
    
    class Meta:
        verbose_name = 'Committee Announcement'
        verbose_name_plural = 'Committee Announcements'
        ordering = ['-date_posted']
        indexes = [
            models.Index(fields=['committee', '-date_posted']),
            models.Index(fields=['is_published', '-date_posted']),
        ]


# ============================================================================
# RESOURCE & CPD MODELS
# ============================================================================

class Resource(models.Model):
    """
    Downloadable resources with access control based on membership tier.
    """
    
    ACCESS_LEVELS = [
        ('public', 'General/Public'),
        ('student', 'Student Only'),
        ('associate', 'Associate & Above'),
        ('full', 'Full Members & Above'),
        ('fellow', 'Fellows Only'),
    ]

    CATEGORIES = [
        ('guideline', 'Clinical Guideline'),
        ('academic', 'Study Material'),
        ('research', 'Research Paper'),
        ('governance', 'Academy Document'),
        ('legal', 'Legal/Ethics'),
        ('general', 'General Information'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        default='general',
        db_index=True
    )
    file = models.FileField(upload_to='resources/')
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVELS,
        default='public',
        db_index=True
    )
    is_verified_only = models.BooleanField(
        default=True,
        help_text="Only verified members can download"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"[{self.get_access_level_display()}] {self.title}"

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Resource'
        verbose_name_plural = 'Resources'
        indexes = [
            models.Index(fields=['category', 'access_level']),
        ]


class CPDRecord(models.Model):
    """
    Continuing Professional Development activity records.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cpd_records'
    )
    activity_name = models.CharField(
        max_length=255,
        help_text="e.g., NAA Annual Conference 2026"
    )
    date_completed = models.DateField(db_index=True)
    points = models.PositiveIntegerField(default=5)
    certificate = models.FileField(
        upload_to='cpd_certificates/',
        null=True,
        blank=True,
        help_text="Upload PDF proof of participation"
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Admin verification status"
    )
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_name} ({self.points} pts)"

    class Meta:
        verbose_name = 'CPD Record'
        verbose_name_plural = 'CPD Records'
        ordering = ['-date_completed']
        indexes = [
            models.Index(fields=['user', '-date_completed']),
            models.Index(fields=['is_verified']),
        ]


# ============================================================================
# COMMITTEE REPORT MODEL
# ============================================================================

class CommitteeReport(models.Model):
    """
    Official reports submitted by committee directors.
    """
    committee = models.ForeignKey(
        Committee,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='committee_reports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.committee.name} - {self.title}"
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Committee Report'
        verbose_name_plural = 'Committee Reports'
        indexes = [
            models.Index(fields=['committee', '-uploaded_at']),
        ]


# ============================================================================
# ARTICLE MODEL
# ============================================================================

class Article(models.Model):
    """
    Journal articles for the NAA publication.
    """
    
    STATUS_CHOICES = [
        ('draft', 'Draft/Pending Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    content = CKEditor5Field(config_name='default')
    image = CloudinaryField(
        'image',
        blank=True,
        null=True,
        folder='articles'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title"""
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Article.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        indexes = [
            models.Index(fields=['status', 'is_public', '-created_at']),
            models.Index(fields=['slug']),
        ]


# ============================================================================
# NOTIFICATION MODEL
# ============================================================================

class Notification(models.Model):
    """
    User notifications displayed on dashboard.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = CKEditor5Field(config_name='default')
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', '-created_at']),
        ]


# ============================================================================
# EMAIL & ABOUT PAGE MODELS
# ============================================================================

class EmailUpdate(models.Model):
    """
    Email templates for bulk sending to members.
    """
    title = models.CharField(
        max_length=200,
        unique=True,
        help_text="Internal name for admins"
    )
    subject = models.CharField(max_length=255)
    message = models.TextField(help_text="Email body (supports {{username}} placeholder)")
    sendgrid_template_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="SendGrid dynamic template ID"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only one template can be active at a time"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Email Template'
        verbose_name_plural = 'Email Templates'


class AboutPage(models.Model):
    """
    Content for the About page (singleton model).
    """
    title = models.CharField(max_length=200, default="About the Academy")
    history_text = CKEditor5Field(config_name='default')
    history_image = CloudinaryField(
        'history image',
        blank=True,
        null=True
    )
    mission = CKEditor5Field(config_name='default')
    vision = CKEditor5Field(config_name='default')
    aims_and_objectives = CKEditor5Field(config_name='default')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = 'About Page Content'


# ============================================================================
# EMAIL HELPER FUNCTIONS
# ============================================================================

def send_verification_email(user):
    """
    Send verification email to newly verified user.
    
    Args:
        user: User instance
    """
    email_template = EmailUpdate.objects.filter(
        title__icontains="Verification"
    ).first()

    if not email_template or not email_template.sendgrid_template_id:
        logger.warning(f"No SendGrid template found for verification email")
        return

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=user.email
    )
    
    message.template_id = email_template.sendgrid_template_id
    message.dynamic_template_data = {
        'subject': email_template.subject,
        'username': user.username,
        'body_text': email_template.message,
    }

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        logger.info(f"Verification email sent to {user.email}")
    except Exception as e:
        logger.error(f"SendGrid error: {e}")


def send_custom_template_email(user, email_update_obj, context=None):
    """
    Send custom email template to user with optional context.
    
    Args:
        user: User instance
        email_update_obj: EmailUpdate instance
        context: Optional dict of additional template variables
    
    Returns:
        bool: True if email sent successfully
    """
    if not email_update_obj.sendgrid_template_id or not user.email:
        return False

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=user.email
    )
    message.template_id = email_update_obj.sendgrid_template_id
    
    # Build template data
    template_data = {
        'subject': email_update_obj.subject,
        'username': user.username,
        'body_text': email_update_obj.message,
    }
    
    # Merge additional context if provided
    if context:
        template_data.update(context)
    
    message.dynamic_template_data = template_data

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        logger.info(f"Email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Email send error: {e}")
        return False