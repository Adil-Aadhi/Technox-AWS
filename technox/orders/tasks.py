from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Orders

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def send_order_confirmation_email(self, order_id):
    order = (
        Orders.objects
        .select_related("user")
        .prefetch_related("order_items__product")
        .get(id=order_id)
    )

    # ✅ Build product list
    product_lines = []
    for item in order.order_items.all():
        product_lines.append(
            f"- {item.product.name} × {item.quantity}"
        )

    product_details = "\n".join(product_lines)

    message = (
        f"Hello {order.user.username},\n\n"
        f"Your order {order.order_id} has been confirmed.\n\n"
        f" Products:\n{product_details}\n\n"
        f" Payment Method: {order.payment_method}\n"
        f" Total Amount: ₹{order.amount}\n\n"
        "Thank you for shopping with us!"
    )

    send_mail(
        subject="Order Confirmed ",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
    )
