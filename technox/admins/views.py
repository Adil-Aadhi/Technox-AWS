from django.shortcuts import render
from .serializers import UserViewSerializer,UserStatusSerializer
from rest_framework.views import APIView
from authentications.models import UserModel
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from orders.models import OrderItem,Orders
from django.db.models import Count,Sum
from django.db.models.functions import Coalesce
from django.db.models import Q

# Create your views here.
class UserView(APIView):
    permission_classes = [IsAdminUser]

    def get(self,request):

        search=request.GET.get('search','')
        status_filter=request.GET.get('status','')

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit

        qs=UserModel.objects.filter(role='user')

        if search:
            qs=qs.filter(Q(name__icontains=search)|
                         Q(email__icontains=search)|
                         Q(id__icontains=search))
            
        if status_filter=='Active':
            qs=qs.filter(status="active")
        elif status_filter=="Inactive":
            qs=qs.filter(status="inactive")
        


        qs=qs.annotate(order_count=Count('orders',distinct=True),product_count=Coalesce(Count('orders__order_items',distinct=True),0))

        total_users=qs.count()
        paginated_qs = qs[offset: offset + limit]

        serializer=UserViewSerializer(paginated_qs, many=True) 
        return Response({"users": serializer.data,"user_count":total_users,"page": page,"limit": limit,"has_next": offset + limit < total_users,"has_prev": page > 1},status=status.HTTP_200_OK)
    
    def patch(self,request,pk):

        try:
            user=UserModel.objects.get(id=pk)
        except UserModel.DoesNotExist:
            return Response({"error": "User not found"},status=status.HTTP_404_NOT_FOUND)
         
        status_data={"status": request.data.get("status")}
        serializer=UserStatusSerializer(user,data=status_data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"succesfully patched"},status=status.HTTP_200_OK)
        return Response(serializer.errors,{"message":"not patched"},status=status.HTTP_400_BAD_REQUEST) 
        