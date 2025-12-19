from django.urls import path
from .views import HomeProducts,AllProducts,SearchProduct,ProductDetails,AdminProducts,AdminProductAdd,AdminProductHide,AdminProductSoftDelete,AdminSoftDeletedProducts,AdminProductsCount

urlpatterns = [
    path('home/',HomeProducts.as_view()),
    path('',AllProducts.as_view()),
    path('admin-products/',AdminProducts.as_view()),
    path('admin-products/count/',AdminProductsCount.as_view()),
    path('admin-products/addproduct/',AdminProductAdd.as_view()),
    path('admin-products/addproduct/<str:id>/',AdminProductAdd.as_view()),
    path('admin-products/hideproduct/<str:id>/',AdminProductHide.as_view()),
    path('admin-products/deleteproduct/<str:id>/',AdminProductSoftDelete.as_view()),
    path('admin-products/deleted-products/',AdminSoftDeletedProducts.as_view()),
    path('admin-products/deleted-products/<str:id>/',AdminSoftDeletedProducts.as_view()),
    path('search/',SearchProduct.as_view()),
    path('details/<str:id>/',ProductDetails.as_view()),
]