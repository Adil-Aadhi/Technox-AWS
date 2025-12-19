from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.utils import timezone

# Create your models here.
class UserModel(AbstractUser):
    name=models.CharField(max_length=150,null=True,blank=True)
    email=models.EmailField(unique=True)
    role=models.CharField(max_length=20,default='user')
    status=models.CharField(max_length=20,default='active')
    profile=models.ImageField( storage=MediaCloudinaryStorage(),upload_to='profiles/', null=True, blank=True)
    sign_date=models.DateField(auto_now_add=True)


    USERNAME_FIELD='username'

    def __str__(self):
        return self.username
    
class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # OTP valid for 5 minutes
        return timezone.now() > self.created_at + timezone.timedelta(minutes=5)

    def __str__(self):
        return f"{self.email} - {self.otp}"

