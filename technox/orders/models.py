from django.db import models
from authentications.models import UserModel
from users.models import UserAddress
from products.models import Product

# Create your models here.
class Orders(models.Model):
    STATUS_CHOICES = [
        ("Payment Pending", "Payment Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user=models.ForeignKey(UserModel, on_delete=models.CASCADE,related_name="orders")
    order_id=models.CharField(max_length=50,unique=True)
    date=models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    address=models.ForeignKey(UserAddress, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Payment Pending")
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=30,blank=True,null=True)
    paid_at = models.DateTimeField(blank=True,null=True)
    razorpay_order_id = models.CharField(max_length=150,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=150,blank=True,null=True)

    def __str__(self):
        return self.order_id
    
class OrderItem(models.Model):
    order=models.ForeignKey(Orders,on_delete=models.CASCADE,related_name="order_items")
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    price=models.DecimalField(max_digits=12,decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"