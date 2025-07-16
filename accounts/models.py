from django.db import models
from django.contrib.auth.models import User
from base.models import BaseModel
# for add to cart
from product.models import Color_varient,Size_varient,Product
from django.dispatch import receiver
import uuid
from base.email import send_account_activateion_email
from django.db.models.signals import post_save


class Profile(BaseModel):
    #   here Profile model is designed to extend the User model with additional, user-specific data. This is a common pattern in Django when you want to store extra information about a user that doesn't fit into the basic User model (like is_email_verified, email_token, profile_image, bio, location, etc.).

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    is_email_verified = models.BooleanField(default= False)
    email_token = models.CharField(max_length=100 , null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile',default='profile/default.png')

    # for cartcounter
    def get_cart_count(self):
        return CartItems.objects.filter(cart__is_paid=False, cart__user = self.user).count()


#  card models
class Cart(BaseModel):
    #  here user who placcing order is connecting to login user through forenkey 
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='carts')
    is_paid = models.BooleanField(default=False)


    #  it calculate the total price of products that are selected inside the cart_items
    def get_cart_total(self):
        cart_items = self.cart_items.all()
        total=0
        for cart_item in cart_items:
            price = cart_item.product.price
            if cart_item.color_varient:
                price += cart_item.color_varient.price
            if cart_item.size_varient:
                price += cart_item.size_varient.price
            total+=price*cart_item.quantity
        return total

# CartItems is list of all items that added to card 
class CartItems(BaseModel):
    # cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items") adds a reverse relationship from Cart to CartItems using the name cart_items.
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="cart_items")
    product=models.ForeignKey(Product,on_delete=models.SET_NULL,null=True,blank=True )
    color_varient= models.ForeignKey(Color_varient,on_delete=models.SET_NULL,null=True,blank=True)
    size_varient= models.ForeignKey(Size_varient,on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.IntegerField(default=1)
 
 #   We use ForeignKeys to each model so that:Each item can track exactly what was ordered (product + size + color).


 #  for total price 
 #  this function calculate the total price of specific product along with different varient 
    def get_product_price(self):
            
        print("DEBUG:")
        print("  Product:", self.product)
        print("  Size Varient:", self.size_varient)
        print("  Color Varient:", self.color_varient)
        price = self.product.price
        total=0
        if self.color_varient:
            price+=self.color_varient.price
        elif self.size_varient:
            price+=self.size_varient.price
    
        total= price*self.quantity
        return total
            

@receiver(post_save, sender = User)
def send_email_token(sender, instance , created, **kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user= instance, email_token=email_token)
            # email = instance.email
            send_account_activateion_email(instance.email, email_token)
    except Exception as e :
        print(e)    






 