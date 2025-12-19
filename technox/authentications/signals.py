from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from authentications.models import UserModel
from .tasks import send_registration_email_task

@receiver(post_save, sender=UserModel)

# def send_registration_email(sender, instance, created, **kwargs):
#     if created and instance.email:
#         try:
#             send_mail(
#                 subject="Registration Successful ",
#                 message=(
#                     f"Hello {instance.username},\n\n"
#                     "You have registered successfully."
#                 ),
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[instance.email],
#             )
#         except Exception as e:
#             # Log error but NEVER break user creation
#             print("Email failed:", e)




def send_registration_email(sender, instance, created, **kwargs):
    if created and instance.email:
        send_registration_email_task.delay(
            instance.email,
            instance.username
        )