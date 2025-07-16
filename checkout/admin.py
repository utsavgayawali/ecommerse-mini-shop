from django.contrib import admin
from .models import ShippingAddress,Order,OrderItems

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItems)
