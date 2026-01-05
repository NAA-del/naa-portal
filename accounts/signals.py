from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def send_verification_email(sender, instance, created, **kwargs):
    # We only send the email if the user is NOT a new creation 
    # and their status has just been changed to is_verified=True
    if not created and instance.is_verified:
        subject = 'Congratulations! Your NAA Membership is Verified'
        message = f"""
Hi {instance.username},

Great news! The Nigerian Academy of Audiology (NAA) has verified your membership.

You now have full access to:
- Your Digital Membership ID
- The Student Hub (for Students)
- The CPD Portfolio Tracker (for Professionals)

Login here: http://127.0.0.1:8000/login/

Welcome to the Academy!
Best regards,
The NAA Admin Team
        """
        email_from = settings.DEFAULT_FROM_EMAIL
        recipient_list = [instance.email]
        
        try:
            send_mail(subject, message, email_from, recipient_list)
        except Exception as e:
            print(f"Error sending email: {e}")