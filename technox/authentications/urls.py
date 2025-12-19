from django.urls import path
from .views import RegistrationUser,LoginUser,CookieRefreshToken,LogoutUser,SendOTPView,VerifyOTPView,ResetPasswordView

urlpatterns = [
    path('register/',RegistrationUser.as_view()),
    path('login/',LoginUser.as_view()),
    path('logout/',LogoutUser.as_view()),
    path("token/refresh-cookie/", CookieRefreshToken.as_view()),
    path("forgot-password/send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("forgot-password/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("forgot-password/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
]
