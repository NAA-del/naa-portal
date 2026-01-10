from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from cloudinary.models import CloudinaryField
import logging

logger = logging.getLogger(__name__)

# --- Helper Function for Email ---
def send_verification_email(user):
    try:
        send_mail(
            'Account Verified - NAA',
            f'Hello {user.first_name},\n\nYour Nigerian Academy of Audiology account has been verified. You can now log in to access member resources.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"Verification email sent to {user.email}")
    except Exception as e:
        # This catch prevents the Admin panel from crashing (Internal Server Error)
        logger.error(f"Email failed to send to {user.email}: {e}")
        print(f"Email error: {e}")

# --- Models ---

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

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Leader(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = CloudinaryField('image')

    def __str__(self):
        return f"{self.name} - {self.position}"

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
    history_text = models.TextField()
    history_image = CloudinaryField('history image', blank=True, null=True)
    mission = models.TextField()
    vision = models.TextField()
    aims_and_objectives = models.TextField()

    class Meta:
        verbose_name_plural = "About Page Content"

    def __str__(self):
        return self.title

class StudentAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    target_university = models.CharField(
        max_length=20, 
        choices=[('All', 'All Universities'), ('UNIMED', 'UNIMED'), ('FUHSI', 'FUHSI'), ('FUHSA', 'FUHSA')],
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