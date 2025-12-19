from rest_framework import serializers
from .models import OrderItem,Orders
from products.serializers import ProductSerializer
from products.models import Product
from django.db import transaction
from rest_framework.exceptions import ValidationError
import uuid
from users.serializers import UserAddressReadSerializer
from users.models import UserAddress
from authentications.serializers import UserModel

class OrderItemSerializer(serializers.ModelSerializer):
    product=ProductSerializer(read_only=True)

    class Meta:
        model=OrderItem
        fields ='__all__'


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    address=UserAddressReadSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=UserAddress.objects.all(),
        source="address",
        write_only=True
    )

    class Meta:
        model=Orders
        fields = '__all__'
        read_only_fields = ["user","order_id"] 
    
    def create(self, validated_data):
        user = self.context.get('user')
        items = self.initial_data.get("items", [])

        if not items:
            raise serializers.ValidationError({"items": "No items provided"})

        validated_data.pop("items", None)

        with transaction.atomic():

            # ✅ FIRST: validate all products & stock
            products_data = []

            for item in items:
                product_id = item.get("product_id")
                quantity = item.get("quantity", 1)

                try:
                    product = Product.objects.select_for_update().get(id=product_id)
                except Product.DoesNotExist:
                    raise serializers.ValidationError(
                        {"product_id": f"Product {product_id} does not exist"}
                    )

                if product.totalquantity < quantity:
                    raise serializers.ValidationError(
                        {"stock": f"Only {product.totalquantity} left for {product.name}"}
                    )

                products_data.append((product, quantity))

            # ✅ SECOND: create order only if ALL products are valid
            order = Orders.objects.create(
                user=user,
                order_id=f"ODR{uuid.uuid4().hex[:10]}",
                **validated_data
            )

            # ✅ THIRD: create order items & update stock
            for product, quantity in products_data:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )

                # product.totalquantity -= quantity
                # product.save()

        return order
    
class AdminOrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "price"
        ]

class AdminOrderViewSerializer(serializers.ModelSerializer):
    products = AdminOrderItemSerializer(source="order_items",many=True,read_only=True)
    address=UserAddressReadSerializer()

    class Meta:
        model=Orders
        fields='__all__'