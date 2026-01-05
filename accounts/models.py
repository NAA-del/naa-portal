from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

# This allows you to add Announcements from the Admin Panel
class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

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
    is_verified = models.BooleanField(default=False) # Admin must check their license first

# This allows you to manage the Executive Council
class Leader(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100) # e.g., President, General Secretary
    image = models.ImageField(upload_to='leaders/')

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
    is_public = models.BooleanField(default=False, help_text="Can anyone see this?")
    is_verified_only = models.BooleanField(default=True, help_text="Only verified members can download")

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About the Academy")
    history_text = models.TextField(help_text="The history of NAA")
    history_image = models.ImageField(upload_to='about/', blank=True, null=True)
    mission = models.TextField()
    vision = models.TextField()
    aims_and_objectives = models.TextField(help_text="Separate objectives with a new line")

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
        return self.titles

class CPDRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cpd_records')
    activity_name = models.CharField(max_length=255)
    points = models.IntegerField()
    date_completed = models.DateField()
    certificate = models.FileField(upload_to='cpd_certs/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_name}"