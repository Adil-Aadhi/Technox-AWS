from rest_framework import serializers
from .models import Cart,Wishlist,UserAddress
from products.serializers import ProductSerializer
from django.contrib.auth import get_user_model
from authentications.serializers import RegisterSerializer

User=get_user_model()

class WishlistSerializer(serializers.ModelSerializer):
    product=ProductSerializer()

    class Meta:
        model=Wishlist
        fields='__all__'
        read_only_fields = ['user']

class WishlistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['product']

class CartSerializer(serializers.ModelSerializer):
    product=ProductSerializer(read_only=True)

    class Meta:
        model=Cart
        fields='__all__'

class CartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields=['product','quantity']

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['name','username','email']

class ChangePasswordSerilizer(serializers.Serializer):
    old_password=serializers.CharField()
    new_password=serializers.CharField()
    confirm_password=serializers.CharField()

    def validate(self ,data):
        if data['new_password']!=data['confirm_password']:
            raise serializers.ValidationError("Password must be same")
        return data
    

class UserAddressReadSerializer(serializers.ModelSerializer):

    user=RegisterSerializer()

    class Meta:
        model=UserAddress
        fields='__all__'

    

class UserAddressWriteSerializer(serializers.ModelSerializer):

    
    class Meta:
        model=UserAddress
        fields='__all__'
        extra_kwargs = {
            "user": {"required": False}  # user will be added from request.user
        }

        # 🟢 FIX: Convert empty string "" -> None so clearing field works
    def to_internal_value(self, data):
        for key, value in data.items():
            if value == "":
                data[key] = None
        return super().to_internal_value(data)

    def validate_mobile(self,value):
        if value in ["", None]:
            return None 
        value = str(value)
        if not value.isdigit():
            raise serializers.ValidationError("Mobile number must contain only digit")
        if len(value)!=10:
            raise serializers.ValidationError("Mobile number must contain 10 digit")
        return value
    
    def validate_post(self,value):
        if value in ["", None]:
            return None 
        value = str(value)
        if not value.isdigit():
            raise serializers.ValidationError("Post code must contain only digit")
        if len(value)!=6:
            raise serializers.ValidationError("Post code must contain 6 digit")
        return value

class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["profile"]
 