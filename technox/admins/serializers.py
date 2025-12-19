from rest_framework import serializers
from django.contrib.auth import authenticate
from authentications.models import UserModel 

class UserViewSerializer(serializers.ModelSerializer):
    order_count = serializers.IntegerField(read_only=True)
    product_count = serializers.IntegerField(read_only=True)

    class Meta:
        model=UserModel
        fields = [
            'id',
            'name',
            'username',
            'email',
            'role',
            'status',
            'date_joined',
            'profile',
            'date_joined',
            'order_count',
            'product_count'
        ]
class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["status"]

    def validate_status(self, value):
        if value not in ["active", "inactive"]:
            raise serializers.ValidationError("Invalid status")
        return value