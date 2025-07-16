from django.urls import path,include
from accounts import views
from accounts.views import add_to_cart,cart,remove_cart,cart_quantity,buy_now

urlpatterns = [
    path('register/',views.register_view, name='register_view'),
    path('login/',views.login_view, name='login_view'),
    path('email_view/',views.email_view, name='email_view'),
    path('otp/',views.otp_view, name='otp_view'),
    path('resetpass/',views.resetpass_view, name='resetpass_view'),
    path('logout/',views.logout_view, name='logout_view'),
    path('activate/<email_token>/', views.activate_user, name='activate_user'),
    path('buy_now/<uid>/', buy_now, name='buy_now'),
    path('add_to_cart/<uid>/', add_to_cart, name='add_to_cart'),
    path('remove_cart/<cart_item_uid>/', remove_cart, name='remove_cart'),
    path('cart/', cart, name='cart'),
    path('cart_quantity/<cart_item_uid>/', cart_quantity, name='cart_quantity'),
    path('profile/', views.profile, name='profile'),
    path('/edit_profile/', views.edit_profile, name='edit_profile'),
    

]
