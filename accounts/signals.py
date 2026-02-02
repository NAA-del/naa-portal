from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone
from .models import User, send_verification_email


@receiver(pre_save, sender=User)
def store_old_verification_status(sender, instance, **kwargs):
    if instance.pk:
        instance._old_is_verified = (
            User.objects.filter(pk=instance.pk)
            .values_list("is_verified", flat=True)
            .first()
        )
    else:
        instance._old_is_verified = False


@receiver(post_save, sender=User)
def send_email_when_verified(sender, instance, created, **kwargs):
    if not created and not instance._old_is_verified and instance.is_verified:
        User.objects.filter(pk=instance.pk).update(date_verified=timezone.now())

        send_verification_email(instance)
