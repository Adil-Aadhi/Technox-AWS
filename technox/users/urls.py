from django.urls import path
from .views import WishlistProducts,CartProducts,UpdateProfile,ChangePassword,AddressUser,ProfileImageUpdateView,UserProfileView,ClearOrderedCartItems

urlpatterns = [
    path('wishlist/<int:id>/',WishlistProducts.as_view()),
    path('wishlist/',WishlistProducts.as_view()),

    path('cart/<int:id>/',CartProducts.as_view()),
    path('cart/',CartProducts.as_view()),
    path('cart/clear-cart/',ClearOrderedCartItems.as_view()),

    path('updateprofile/',UpdateProfile.as_view()),
    path('updatepassword/',ChangePassword.as_view()),
    
    path('address/',AddressUser.as_view()),

    path("profile-image/", ProfileImageUpdateView.as_view(), name="profile-image"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]