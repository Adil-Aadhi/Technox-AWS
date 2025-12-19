from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage
import uuid

# Create your models here.
class Product(models.Model):
    id=models.CharField(primary_key=True,max_length=50,default=uuid.uuid4,editable=False)
    name=models.CharField(max_length=255)
    brand=models.CharField(max_length=100)

    price=models.IntegerField()
    type=models.CharField(max_length=100)

    storage=models.CharField(max_length=50)
    ram=models.CharField(max_length=50)
    color=models.CharField(max_length=50)

    image=models.ImageField(storage=MediaCloudinaryStorage(),upload_to='products/',blank=True,null=True)

    display=models.CharField(max_length=255)
    cpu=models.CharField(max_length=100)

    description=models.TextField()

    status=models.CharField(max_length=20, default="active")
    totalquantity = models.IntegerField()

    def __str__(self):
        return self.name