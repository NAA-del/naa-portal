from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
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
    membership_tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if this is an update to an existing user
        if self.pk:
            old_user = User.objects.get(pk=self.pk)
            # If is_verified was False and is now True, send the email
            if not old_user.is_verified and self.is_verified:
                send_verification_email(self)
        
        super().save(*args, **kwargs)

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Leader(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='leaders/')

    def __str__(self):
        return f"{self.name} - {self.position}"

class StudentProfile(models.Model):
    UNIVERSITY_CHOICES = [
        ('UNIMED', 'University of Medical Sciences, Ondo (UNIMED)'),
        ('FUHSI', 'Federal University of Health Sciences, Ila-Orangun (FUHSI)'),
        ('FUHSA', 'Federal University of Health Sciences, Azare (FUHSA)'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_info')
    university = models.CharField(max_length=100, choices=UNIVERSITY_CHOICES)
    matric_number = models.CharField(max_length=20, unique=True)
    level = models.IntegerField(choices=[(100, '100L'), (200, '200L'), (300, '300L'), (400, '400L'), (500, '500L')])
    
    def __str__(self):
        return f"{self.user.username} ({self.university})"

class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('student', 'Student Resource'),
        ('clinical', 'Clinical Guidelines'),
        ('research', 'Research Papers'),
        ('admin', 'Administrative Docs'),
    ]
    
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to='resources/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    is_verified_only = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About the Academy")
    history_text = models.TextField()
    history_image = models.ImageField(upload_to='about/', blank=True, null=True)
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