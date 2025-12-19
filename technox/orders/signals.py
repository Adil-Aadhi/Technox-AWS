from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from .models import Orders
from .tasks import send_order_confirmation_email  # celery task

@receiver(post_save, sender=Orders)
def order_confirmation_handler(sender, instance, created, **kwargs):
  

    # 🔒 Prevent duplicate emails
    if getattr(instance, "_email_sent", False):
        return

    is_cod_confirmed = (
        instance.payment_method == "COD"
        and instance.status == "Processing"
    )

    is_razorpay_confirmed = (
        instance.payment_method == "RAZORPAY"
        and instance.is_paid
    )

    if is_cod_confirmed or is_razorpay_confirmed:
        try:
            send_order_confirmation_email.delay(instance.id)
        except Exception as e:
            # 🔕 Silent fail (log only)
            print("Celery/Redis not available:", e)
            
        instance._email_sent = True
