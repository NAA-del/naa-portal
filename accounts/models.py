from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from cloudinary.models import CloudinaryField
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

logger = logging.getLogger(__name__)

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
    sendgrid_template_id = models.CharField(max_length=100, blank=True, null=True, help_text="d-55d095291d714497a445e6f9768ffd31")
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk:
            # Check if is_verified is changing from False to True
            old_user = User.objects.get(pk=self.pk)
            if not old_user.is_verified and self.is_verified:
                send_verification_email(self)
        
        super().save(*args, **kwargs)

def send_verification_email(user):
    email_template = EmailUpdate.objects.filter(
        is_active=True, 
        title__icontains="Verification"
    ).first()

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

class EmailUpdate(models.Model):
    title = models.CharField(max_length=200, help_text="Internal name for admins")
    subject = models.CharField(max_length=255)
    message = models.TextField(help_text="Email body (plain text for now)")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

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