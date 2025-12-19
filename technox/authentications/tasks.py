from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task(bind=True, max_retries=3)
def send_registration_email_task(self, email, username):
    try:
        send_mail(
            subject="Registration Successful",
            message=f"Hello {username},\n\nYou have registered successfully.\n Welcome to Technox family",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
    except Exception as e:
        raise self.retry(exc=e, countdown=10)