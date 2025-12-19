from django.urls import path
from .views import UserOrderView,RazorpayCreateOrder,RazorpayVerifyPayment,AdminOrdersVIew

urlpatterns = [

    path('admin-orders/',AdminOrdersVIew.as_view()),
    path('admin-orders/<str:order_id>/',AdminOrdersVIew.as_view()),

    path('',UserOrderView.as_view()),
    path('<str:order_id>/',UserOrderView.as_view()),

    path("payment/razorpay/create/", RazorpayCreateOrder.as_view()),
    path("payment/razorpay/verify/", RazorpayVerifyPayment.as_view()),
]