from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
from product.models import Product




class ShippingAddress(BaseModel):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=225)
    phone_no = models.CharField(max_length=225,null=True,blank=True)
    address_line1= models.CharField(max_length=225)
    address_line2= models.CharField(max_length=225,blank=True, null=True)
    city = models.CharField(max_length=225)
    state = models.CharField(max_length=225)
    zip_code = models.CharField(max_length=225)

    def __str__(self):
        return f"{self.full_name},{self.city}"



class Order(BaseModel):
    # clear 1 why onltoone field not 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # order_id is inherit form uuid of basemodels
    shipping_address = models.ForeignKey(ShippingAddress,on_delete=models.SET_NULL,null= True)
    total_price = models.FloatField()

    def __str__(self):
        return f"{self.user.username}"
    
class OrderItems(BaseModel):
    order= models.ForeignKey(Order,on_delete= models.CASCADE ,related_name='items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()


    def __str__(self):
        return f"{self.product.product_name}"

