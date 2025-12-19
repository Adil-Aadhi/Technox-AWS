from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Orders
from .serializers import OrderSerializer,AdminOrderViewSerializer
from django.db import transaction
import razorpay
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

# Create your views here.

def cleanup_pending_orders():
    cutoff_time = timezone.now() - timedelta(minutes=30)

    Orders.objects.filter(
        is_paid=False,
        status="Payment Pending",
        created_at__lt=cutoff_time
    ).delete()




class UserOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):

        cleanup_pending_orders()

        orders=Orders.objects.filter(user_id=request.user.id).prefetch_related('order_items__product')
        serializer=OrderSerializer(orders, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self,request):
        serializer=OrderSerializer(data=request.data,context={"user": request.user})
        if serializer.is_valid():
            order=serializer.save()
            if order.payment_method == "COD":
                for item in order.order_items.all():
                    product = item.product
                    product.totalquantity -= item.quantity
                    product.save()
                # optional: move status forward
                order.status = "Processing"
                order.save(update_fields=["status"])

            return Response({"order_id": order.order_id,"payment_method": order.payment_method,},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, order_id=None):
        order = Orders.objects.prefetch_related("order_items__product").filter(order_id=order_id,user=request.user).first()

        if not order:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status not in ["Processing"]:
            return Response(
                {"error": "Order cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # ✅ Restore stock
            for item in order.order_items.all():
                product = item.product
                product.totalquantity += item.quantity
                product.save()

            # ✅ Update order status
            order.status = "Cancelled"
            order.save()

        return Response(
            {"message": "Order cancelled successfully"},
            status=status.HTTP_200_OK
        )
    
class RazorpayCreateOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")

        if not order_id:
            return Response(
                {"error": "order_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Orders.objects.filter(
            order_id=order_id,
            user=request.user
        ).first()

        if not order:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.is_paid:
            return Response(
                {"error": "Order already paid"},
                status=status.HTTP_400_BAD_REQUEST
            )

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            "amount": int(order.amount * 100),  # ✅ paise
            "currency": "INR",
            "payment_capture": 1
        })

        order.razorpay_order_id = razorpay_order["id"]
        order.save(update_fields=["razorpay_order_id"])

        return Response({
            "key": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order["id"],
            "amount": int(order.amount * 100),
            "currency": "INR",
        }, status=status.HTTP_200_OK)
    

class RazorpayVerifyPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"]
            })

            order = Orders.objects.filter(
                razorpay_order_id=data["razorpay_order_id"],
                user=request.user
            ).first()

            if not order:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            if order.is_paid:
                return Response(
                    {"message": "Order already paid"},
                    status=status.HTTP_200_OK
                )

            order.is_paid = True
            order.status = "Processing"
            order.payment_method = "RAZORPAY"
            order.razorpay_payment_id = data["razorpay_payment_id"]
            order.paid_at = timezone.now()
            order.save()

            for item in order.order_items.all():
                product = item.product
                product.totalquantity -= item.quantity
                product.save()

            return Response({"message": "Payment verified"}, status=200)

        except Exception:
            return Response(
                {"error": "Payment verification failed"},
                status=400
            )
        

class AdminOrdersVIew(APIView):

    def get(self,request):
        orders=Orders.objects.prefetch_related("order_items__product")

        status_filter = request.GET.get("statusFilter")
        search=request.GET.get('search')

        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        offset = (page - 1) * limit

        status_counts = (
            Orders.objects
            .values("status")
            .annotate(count=Count("id"))
        )

        counts = {item["status"]: item["count"] for item in status_counts}

        total_order_count=orders.count()

        if search:
            orders=orders.filter(order_id__icontains=search)

        if status_filter:
            orders=orders.filter(status=status_filter)

        paginated_orders = orders[offset: offset + limit]

        serializers=AdminOrderViewSerializer(paginated_orders,many=True)
        return Response({"orders":serializers.data,"status_counts": counts,"total_order_count":total_order_count,"page": page,"limit": limit,"has_next": offset + limit < total_order_count,"has_prev": page > 1,},status=status.HTTP_200_OK)
    
    def patch(self,request,order_id):
        order_ids=order_id
        order=Orders.objects.filter(order_id=order_ids).first()
        serializer=OrderSerializer(order,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)