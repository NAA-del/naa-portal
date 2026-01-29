from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django_ckeditor_5.fields import CKEditor5Field
from cloudinary.models import CloudinaryField
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

logger = logging.getLogger(__name__)

class Role(models.Model):
    name = models.CharField(max_length=100) # e.g., "EXCO", "Trustee (BoT)", "Committee Director"
    permissions_level = models.IntegerField(default=1) # To rank authority

    def __str__(self):
        return self.name

class Committee(models.Model):
    name = models.CharField(max_length=100) # e.g., "SCOPHA", "Education Committee"
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='committees')
    director = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='directed_committees')

    def __str__(self):
        return self.name

class User(AbstractUser):
    TIER_CHOICES = [
        ('student', 'Student Member'),
        ('associate', 'Associate Member'),
        ('full', 'Full Member'),
        ('fellow', 'Fellow'),
    ]
    profile_picture = CloudinaryField('image', null=True, blank=True)
    membership_tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)
    date_verified = models.DateTimeField(null=True, blank=True, editable=False)
    roles = models.ManyToManyField(Role, blank=True, related_name='users')

    def save(self, *args, **kwargs):
        if self.pk:
            pass
            
        super().save(*args, **kwargs)
        
class Executive(models.Model):
    # Relational Foundation: Links to a real User account
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='executive_profile'
    )
    
    # Information fields
    position = models.CharField(max_length=100, help_text="e.g., National President")
    bio = models.TextField(
        blank=True, 
        null=True, 
        help_text="A short introductory text about the officer (shows on Home Page)."
    )
    rank = models.PositiveIntegerField(default=1, help_text="Used to order them (1 for President, 2 for VP, etc.)")
    
    # The 'When': Tracking the starting date
    term_start_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['rank'] # Ensures they appear in the correct order of authority

    def __str__(self):
        return f"{self.position} - {self.user.get_full_name() or self.user.username}"

def send_verification_email(user):
    
    email_template = EmailUpdate.objects.filter(title__icontains="Verification").first()

    # 2. Safety check: If no template or ID is found, stop or use fallback
    if not email_template or not email_template.sendgrid_template_id:
        logger.warning(f"No SendGrid Template found in Admin for verification.")
        return

    # 3. Build the SendGrid Message
    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=user.email
    )
    
    message.template_id = email_template.sendgrid_template_id

    message.dynamic_template_data = {
        'subject': email_template.subject,
        'username': user.username,
        'body_text': email_template.message,  # Text you wrote in the Admin
    }

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        logger.info(f"SendGrid Dynamic Email sent to {user.email}")
    except Exception as e:
        logger.error(f"SendGrid Error: {e}")

def send_custom_template_email(user, email_update_obj):
    """
    Takes a user and an EmailUpdate object and sends it via SendGrid
    """
    if not email_update_obj.sendgrid_template_id or not user.email:
        return False

    message = Mail(
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_emails=user.email
    )
    message.template_id = email_update_obj.sendgrid_template_id
    message.dynamic_template_data = {
        'subject': email_update_obj.subject,
        'username': user.username,
        'body_text': email_update_obj.message,
    }

    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

class EmailUpdate(models.Model):
    title = models.CharField(max_length=200, help_text="Internal name for admins")
    subject = models.CharField(max_length=255)
    message = models.TextField(help_text="Email body (plain text for now)")
    created_at = models.DateTimeField(auto_now_add=True)
    sendgrid_template_id = models.CharField(max_length=100, blank=True, null=True, help_text="d-55d095291d714497a445e6f9768ffd31")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(blank=True, help_text="Short preview shown on home page")
    content = CKEditor5Field(config_name='default')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    is_published = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    date_posted = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.title

class StudentProfile(models.Model):
    UNIVERSITY_CHOICES = [
        ('UNIMED', 'University of Medical Sciences, Ondo (UNIMED)'),
        ('FUHSI', 'Federal University of Health Sciences, Ila-Orangun (FUHSI)'),
        ('FUHSA', 'Federal University of Health Sciences, Azare (FUHSA)'),
        ('FUDMA', 'Federal University Dutsin-Ma, Katsina (FUDMA)'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='student_info'
    )
    # Changed back to CharField
    university = models.CharField(max_length=100, choices=UNIVERSITY_CHOICES)
    matric_number = models.CharField(max_length=20, unique=True)
    
    level = models.IntegerField(choices=[
        (100, '100L'), (200, '200L'), (300, '300L'), 
        (400, '400L'), (500, '500L')
    ])
    
    def __str__(self):
        return f"{self.user.username} ({self.university})"

class Resource(models.Model):
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
    category = models.CharField(max_length=20, choices=CATEGORIES, default='general')
    file = models.FileField(upload_to='resources/') # Or CloudinaryField('raw') for PDFs
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='public')
    is_verified_only = models.BooleanField(
        default=True, 
        help_text="If checked, only verified members can download this."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"[{self.get_access_level_display()}] {self.title}"

    class Meta:
        ordering = ['-uploaded_at']

class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About the Academy")
    history_text = CKEditor5Field(config_name='default')
    history_image = CloudinaryField('history image', blank=True, null=True)
    mission = CKEditor5Field(config_name='default')
    vision = CKEditor5Field(config_name='default')
    aims_and_objectives = CKEditor5Field(config_name='default')

    class Meta:
        verbose_name_plural = "About Page Content"

    def __str__(self):
        return self.title

class StudentAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    content = CKEditor5Field(config_name='default')
    date_posted = models.DateTimeField(auto_now_add=True)
    target_university = models.CharField(
        max_length=20, 
        choices=[('All', 'All Universities'), ('UNIMED', 'UNIMED'), ('FUHSI', 'FUHSI'), ('FUHSA', 'FUHSA'), ('FUDMA', 'FUDMA')],
        default='All'
    )

    def __str__(self):
        return self.title # Fixed typo: changed self.titles to self.title

class CPDRecord(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='cpd_records'
    )
    activity_name = models.CharField(max_length=255, help_text="e.g., NAA Annual Conference 2026")
    date_completed = models.DateField()
    points = models.PositiveIntegerField(default=5)
    certificate = models.FileField(
        upload_to='cpd_certificates/', 
        null=True, 
        blank=True,
        help_text="Upload PDF or Image proof of participation"
    )
    is_verified = models.BooleanField(default=False, help_text="Admin will check this after reviewing the certificate")
    date_recorded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_name} ({self.points} pts)"

    class Meta:
        verbose_name = "CPD Record"
        verbose_name_plural = "CPD Records"

class Notification(models.Model):
    # Change 'User' to 'settings.AUTH_USER_MODEL'
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = CKEditor5Field(config_name='default')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"

class CommitteeReport(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='reports')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='committee_reports/') # Stored securely
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.committee.name} - {self.title}"
    
class CommitteeAnnouncement(models.Model):
    committee = models.ForeignKey(Committee, on_delete=models.CASCADE, related_name='announcements')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = CKEditor5Field(config_name='default')
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.committee.name}: {self.title}"

class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft/Pending Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = CKEditor5Field(config_name='default')
    image = CloudinaryField('image', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft') # For EXCO review
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title