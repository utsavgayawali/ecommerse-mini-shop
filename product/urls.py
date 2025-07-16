from django.urls import path,include
from product import views

urlpatterns = [
    path('<slug>',views.product, name='product'),
    path('catrgory/<slug>/', views.product_category, name='product_category'),
    path('search/',views.search_view,name='search_view'),

]
