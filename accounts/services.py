from django.conf import settings
from django.core.mail import send_mail
from django.template import Template, Context
from django.urls import reverse
from django.utils.html import strip_tags
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .models import Notification


class EmailService:
    @staticmethod
    def render_text(text, context=None):
        ctx = Context(context or {})
        return Template(text).render(ctx)

    @staticmethod
    def send_via_sendgrid(to_email, subject, html_body, dynamic_data=None, template_id=None):
        if not settings.SENDGRID_API_KEY:
            return False
        message = Mail(from_email=settings.DEFAULT_FROM_EMAIL, to_emails=to_email)
        if template_id:
            message.template_id = template_id
            message.dynamic_template_data = dynamic_data or {}
        else:
            message.subject = subject
            message.html_content = html_body
            message.plain_text_content = strip_tags(html_body)
        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sg.send(message)
            return True
        except Exception:
            return False

    @staticmethod
    def send_basic_email(to_email, subject, body):
        send_mail(subject=subject, message=strip_tags(body), from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[to_email], fail_silently=False)
        return True

    @staticmethod
    def send_verification_email(user, email_update_obj=None):
        site_url = settings.SITE_URL.rstrip("/")
        login_url = site_url + reverse("login")
        profile_url = site_url + reverse("profile")
        if email_update_obj and email_update_obj.sendgrid_template_id:
            data = {
                "subject": email_update_obj.subject,
                "username": user.username,
                "body_text": email_update_obj.message,
                "login_url": login_url,
                "profile_url": profile_url,
                "site_url": site_url,
            }
            sent = EmailService.send_via_sendgrid(user.email, email_update_obj.subject, "", dynamic_data=data, template_id=email_update_obj.sendgrid_template_id)
            if sent:
                return True
        subject = "Your NAA membership verification"
        html_body = EmailService.render_text(email_update_obj.message if email_update_obj else "Hello {{ username }}, your account has been verified. Visit your profile.", {"username": user.username})
        return EmailService.send_basic_email(user.email, subject, html_body)

    @staticmethod
    def send_custom_template_email(user, email_update_obj, context=None):
        site_url = settings.SITE_URL.rstrip("/")
        login_url = site_url + reverse("login")
        profile_url = site_url + reverse("profile")
        base = {
            "subject": email_update_obj.subject,
            "username": user.username,
            "body_text": email_update_obj.message,
            "login_url": login_url,
            "profile_url": profile_url,
            "home_url": site_url,
            "site_url": site_url,
        }
        if context:
            base.update(context)
        if email_update_obj.sendgrid_template_id and settings.SENDGRID_API_KEY:
            sent = EmailService.send_via_sendgrid(user.email, email_update_obj.subject, "", dynamic_data=base, template_id=email_update_obj.sendgrid_template_id)
            if sent:
                return True
        html_body = EmailService.render_text(email_update_obj.message, base)
        return EmailService.send_basic_email(user.email, email_update_obj.subject, html_body)


class NotificationService:
    @staticmethod
    def create(user, title, message, context=None, send_email=False):
        rendered_message = EmailService.render_text(message, {"username": user.username, **(context or {})})
        n = Notification.objects.create(user=user, title=title, message=rendered_message, is_read=False)
        if send_email:
            EmailService.send_basic_email(user.email, title, rendered_message)
        return n
