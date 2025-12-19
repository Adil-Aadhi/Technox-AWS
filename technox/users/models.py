from django.db import models
from products.models import Product
from authentications.models import UserModel

# Create your models here.
class Wishlist(models.Model):
    user=models.ForeignKey(UserModel,on_delete=models.CASCADE,related_name='wishlist_items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='wishlisted_by')
    added_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"
    
class Cart(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="carted_by")
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.product.name} ({self.quantity})"
    
class UserAddress(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name="user_address")
    house_no=models.CharField(max_length=20, blank=True, null=True)
    landmark=models.CharField(max_length=100, blank=True, null=True)
    town=models.CharField(max_length=50, blank=True, null=True)
    district=models.CharField(max_length=100, blank=True, null=True)
    post=models.CharField(max_length=10, blank=True, null=True)
    mobile=models.CharField(max_length=10, blank=True, null=True)


    def __str__(self):
        return self.user.name