from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Product
from rest_framework_simplejwt.tokens import RefreshToken

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model=Product
        fields='__all__'

    def get_image(self, obj):
        if obj.image:
            return obj.image.url  # Cloudinary full URL
        return None
    
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['status']