from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import UserModel
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    
    confirm=serializers.CharField(write_only=True)

    class Meta:
        model=UserModel
        fields=['name','username','email','password','confirm']
        extra_kwargs={
            'password':{'write_only':True}
        }

    
    def validate(self,data):
        if data['password']!=data['confirm']:
            raise serializers.ValidationError('password and confirm password must be same')
        return data
    
    def create(self,validated_data):
        password=validated_data.pop('password')
        validated_data.pop('confirm')

        user=UserModel.objects.create(**validated_data)

        user.set_password(password)
        user.save()
        return user
    
class LoginSerializer(serializers.Serializer):
    identifier=serializers.CharField()
    password=serializers.CharField()

    def validate(self, data):
        username=data.get('identifier')
        password=data.get('password')

        user=authenticate(username=username,password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if user.status == "inactive":
            raise serializers.ValidationError(
                "Your account has been blocked by admin"
            )
        
        refresh=RefreshToken.for_user(user)

        return {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "status": user.status,
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    

class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"error": "Passwords do not match"}
            )
        return data