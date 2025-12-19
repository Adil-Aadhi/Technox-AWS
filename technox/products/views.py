from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer,ProductCreateSerializer,ProductStatusSerializer
from rest_framework.permissions import AllowAny
from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from .pagination import AdminProductPagination
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
class HomeProducts(APIView):
    permission_classes = [AllowAny]
    
    def get(self,request):
        products=Product.objects.exclude(status="delete")[7:17]
        serializer= ProductSerializer(products, many=True)
        return Response(serializer.data)
    
class AllProducts(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductSerializer

    def get_queryset(self):
        products=Product.objects.exclude(status="delete")

        brand=self.request.GET.get('brand')
        types=self.request.GET.get('type')

        if brand:
            products=products.filter(brand__iexact=brand)
        
        if types:
            products=products.filter(type__iexact=types)

        return products
    



class SearchProduct(APIView):
    permission_classes =[AllowAny]

    def get(self,request):
        query=request.GET.get('q','')

        if query.strip()=="":
            return Response([])
        
        Products=Product.objects.exclude(status="delete").filter(
            Q(name__icontains=query)|
            Q(brand=query)
            )
        serializer=ProductSerializer(Products,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class ProductDetails(APIView):
    permission_classes=[AllowAny]

    def get(self,request,id):
        try:
            products=Product.objects.get(id=id)
        except Product.Doesnotexist:
            return Response({"message":"product not found"},status=status.HTTP_400_BAD_REQUEST)
        serializer=ProductSerializer(products)
        return Response(serializer.data,status=status.HTTP_200_OK)
        

class AdminProducts(ListAPIView):
    # permission_classes = [IsAdminUser]
    serializer_class = ProductSerializer
    pagination_class = AdminProductPagination

    def get_queryset(self):
        products = Product.objects.exclude(status="delete")

        brand = self.request.GET.get('brand')
        types = self.request.GET.get('type')
        search = self.request.GET.get('search')


        if brand:
            products = products.filter(brand__iexact=brand)
        
        if types:
            products = products.filter(type__iexact=types)

        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__icontains=search)
            )

        return products

class AdminProductAdd(APIView):
    parser_classes = [MultiPartParser, FormParser] 

    def post(self,request):
        serializers=ProductCreateSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_200_OK)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self,request,id):
        try:
            products=Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"message":"product is not found"},status=status.HTTP_404_NOT_FOUND)
        
        serializer=ProductCreateSerializer(products,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AdminProductHide(APIView):

    def patch(self,request,id):
        try:
            product=Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response("Product is unavailable",status=status.HTTP_400_BAD_REQUEST)
        serializer=ProductCreateSerializer(product,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AdminProductSoftDelete(APIView):

    def patch(self,request,id):
        try:
            product=Product.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"detail": "Product is unavailable"},status=status.HTTP_400_BAD_REQUEST)
        
        status_value = request.data.get("status")

        if status_value is None:
            return Response({"detail": "Status is required"}, status=400)
        
        serializer=ProductStatusSerializer(product,data={"status": status_value},partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class AdminSoftDeletedProducts(APIView):

    def get(self,request):
        Products=Product.objects.filter(status='delete')
        serializer=ProductSerializer(Products,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def patch(self,request,id):
        try:
            product=Product.objects.get(id=id, status='delete')
        except Product.DoesNotExist:
            return Response({"detail": "Product not found or not deleted."},status=status.HTTP_404_NOT_FOUND)
        
        status_value = request.data.get("status")

        if status_value is None:
            return Response({"detail": "Status is required"}, status=400)
        
        serializer=ProductStatusSerializer(product,data={"status": status_value},partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product restored successfully", "data": serializer.data},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AdminProductsCount(APIView):

    def get(self,request):
        total_products=Product.objects.all().count()
        return Response({"Total_products":total_products})