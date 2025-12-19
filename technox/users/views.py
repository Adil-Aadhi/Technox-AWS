from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Wishlist,Cart,UserAddress
from .serializers import CartSerializer,WishlistSerializer,WishlistCreateSerializer,CartCreateSerializer,ProfileUpdateSerializer,ChangePasswordSerilizer,UserAddressReadSerializer,UserAddressWriteSerializer,ProfileImageSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User=get_user_model()

# Create your views here.
class WishlistProducts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,id):
       
        products=Wishlist.objects.select_related('product').filter(user_id=id)
        serializer=WishlistSerializer(products, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        
        product=WishlistCreateSerializer(data=request.data)
        if product.is_valid():
            product.save(user=request.user)
            return Response({"message": "Added to wishlist"},status=status.HTTP_200_OK)
        return Response(product.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,id):
        deleted,_=Wishlist.objects.filter(product_id=id,user=request.user).delete()

        if deleted:
            return Response({"message":"Removed from wishlist"},status=status.HTTP_201_CREATED)
        return Response({"error":"Item not found"},status=status.HTTP_404_NOT_FOUND)   



class CartProducts(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,):
        products=Cart.objects.select_related('product').filter(user_id=request.user.id)
        serialize=CartSerializer(products,many=True)
        return Response(serialize.data)
    
    def post(self,request):
        serializer=CartCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({'message':"Added to cart successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_404_NOT_FOUND)
    
    def delete(self,request,id):
        deleted,_=Cart.objects.filter(product_id=id,user=request.user).delete()
        if deleted:
            return Response({"message":"Removed from Cart"},status=status.HTTP_201_CREATED)
        return Response({"error":"Item not found"},status=status.HTTP_404_NOT_FOUND)
    
    def patch(self,request,id):
        
        try:
            product=Cart.objects.get(product_id=id,user=request.user)
        except Cart.DoesNotExist:
            return Response({"error":"item not found"},status=status.HTTP_400_BAD_REQUEST)
        
        serializer=CartCreateSerializer(product,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class ClearOrderedCartItems(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_ids = request.data.get("product_ids", [])

        if not product_ids:
            return Response(
                {"error": "No product IDs provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        Cart.objects.filter(
            user_id=request.user.id,
            product_id__in=product_ids
        ).delete()

        return Response(
            {"message": "Ordered items removed from cart"},
            status=status.HTTP_200_OK
        )
    
class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self,request):
        serializer=ProfileUpdateSerializer(request.user,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class ChangePassword(APIView):
    permission_classes=[IsAuthenticated]

    def patch(self,request):
        user=request.user
        serializer=ChangePasswordSerilizer(data=request.data)
        if serializer.is_valid():
            old_password=serializer.validated_data['old_password']
            new_password=serializer.validated_data['new_password']

            if not user.check_password(old_password):
                return Response({"error":"old password is incorrect"},status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()

            return Response({"message": "Password updated successfully"},status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AddressUser(APIView):

    def get(self,request):
        address=UserAddress.objects.filter(user_id=request.user.id).first()

        if not address:
            return Response({"message": "No address found"}, status=404)
        serializer=UserAddressReadSerializer(address)
        return Response(serializer.data)
    
    def patch(self,request):

        address=UserAddress.objects.filter(user_id=request.user.id).first()
        
        if address:
            serializer=UserAddressWriteSerializer(address,data=request.data,partial=True)
        else:
            serializer=UserAddressWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"message":"address inserted"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class ProfileImageUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = ProfileImageSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Image updated successfully", "profile_image": user.profile.url if user.profile else None})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "username": user.username,
            "profile": user.profile.url if user.profile else None
        })