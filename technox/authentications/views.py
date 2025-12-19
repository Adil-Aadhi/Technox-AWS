from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import RegisterSerializer,LoginSerializer,SendOTPSerializer,VerifyOTPSerializer,ResetPasswordSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import UserModel,EmailOTP
import random
from django.core.mail import send_mail
from django.utils import timezone

# Create your views here.
class RegistrationUser(APIView):
    def post(self,request):
        user=RegisterSerializer(data=request.data)
        if user.is_valid():
            user.save()
            return Response(user.data,status=status.HTTP_201_CREATED)
        return Response(user.errors,status=status.HTTP_400_BAD_REQUEST)
    

class LoginUser(APIView):
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            data=serializer.validated_data

            access=data['access']
            refresh=data['refresh']
            user=data['user']

            response=Response({
                "message": "Login successful",
                "access": access,
                "user": user
            }, status=status.HTTP_200_OK)

            # Set HttpOnly cookie for refresh token
            response.set_cookie(
                key='refresh',
                value=refresh,
                httponly=True,
                secure=False,
                samesite='None',
                max_age=7 * 24 * 60 * 60, 
                path="/" ,
            )
            return response
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    #gpt
    
class CookieRefreshToken(APIView):
    def post(self, request):
        old_refresh = request.COOKIES.get("refresh")
        print(old_refresh)
        if not old_refresh:
            return Response({"detail": "Refresh token missing"}, status=401)

        try:
            refresh = RefreshToken(old_refresh)


            access = refresh.access_token

            response = Response({"access": str(access)}, status=200)

            return response

        except Exception:
            return Response({"detail": "Invalid or expired refresh"}, status=401)
        
class LogoutUser(APIView):

    def post(self,request):
        
            refresh_token=request.COOKIES.get('refresh')
            response = Response({"message": "Logged out"}, status=200)

            if refresh_token:
                try:
                    token=RefreshToken(refresh_token)
                    token.blacklist()
                except:
                    pass

            response.delete_cookie(
                "refresh",
                path="/",
                samesite="None",
            )

            return response
    
class SendOTPView(APIView):
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        # 1️⃣ Check email exists in User model
        if not UserModel.objects.filter(email=email).exists():
            return Response(
                {"error": "This email is not registered"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2️⃣ Generate random 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # 3️⃣ Save or update OTP in DB
        EmailOTP.objects.update_or_create(
            email=email,
            defaults={"otp": otp, "created_at": timezone.now()}
        )

        # 4️⃣ Send OTP to email
        send_mail(
            subject="Your Password Reset OTP",
            message=f"Your OTP is {otp}. It is valid for 5 minutes.",
            from_email=None,        # uses DEFAULT_FROM_EMAIL
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {"message": "OTP sent to your email"},
            status=status.HTTP_200_OK
        )
    

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        # 1️⃣ Get OTP record
        try:
            otp_obj = EmailOTP.objects.get(email=email)
        except EmailOTP.DoesNotExist:
            return Response(
                {"error": "No OTP requested for this email"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2️⃣ Check expiry
        if otp_obj.is_expired():
            otp_obj.delete()
            return Response(
                {"error": "OTP expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3️⃣ Check OTP match
        if otp_obj.otp != otp:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )
        otp_obj.delete()

        return Response(
            {"message": "OTP verified successfully"},
            status=status.HTTP_200_OK
        )

class ResetPasswordView(APIView):

    def post(self,request):
        serializer=ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]

        try:
            user=UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return Response( {"error": "User not found"},status=status.HTTP_400_BAD_REQUEST)
        
        if EmailOTP.objects.filter(email=email).exists():
            return Response(
                {"error": "OTP verification required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK
        )


