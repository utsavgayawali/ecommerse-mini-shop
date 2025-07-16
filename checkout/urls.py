from django.urls import path,include
from checkout import views

urlpatterns = [
     path('shipping_address/',views.shipping_address,name='shipping_address'),
     path('make_purchese/',views.make_purchese,name='make_purchese'),
     path('checkout/',views.checkout,name='checkout'),

] 