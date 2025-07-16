from django.shortcuts import render,redirect,HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout,authenticate
import random
from django.core.mail import send_mail
from django.conf import settings

from .models import Profile,CartItems,Cart
from product.models import Size_varient,Product
from django.contrib.auth.decorators import login_required
from checkout.models import ShippingAddress,Order,OrderItems




def register_view(request):
    if request.method == "POST":
        first_name= request.POST.get('first_name')
        last_name= request.POST.get('last_name')
        email= request.POST.get('email')
        password= request.POST.get('password')
        
        user_data_has_error = False

        if User.objects.filter(email=email).exists():
            user_data_has_error=True
            messages.error(request,'Email already exist !')
            return redirect('register_view')
        
        try:
            validate_password(password,user=None)
        except ValidationError as e:
            user_data_has_error=True
            for error_message in e.messages:
                messages.error(request,error_message)

        if user_data_has_error:
            return redirect('register_view')
        else:
            user=User.objects.create_superuser(first_name=first_name,last_name=last_name,email=email,password=password,username=email)
            user.is_active=True
            user.is_staff =True
            user.is_superuser=True
            user.save()
        
            messages.success(request,'An email has been send sucessfully on your mail.Activate Your account')

    return render(request,'accounts/register.html')



def login_view(request):
     if request.method == "POST":
        email= request.POST.get('email')
        password= request.POST.get('password')
        user_obj = User.objects.filter(username=email)

        if  not user_obj[0].profile.is_email_verified:
            messages.error(request,'Account not verified !')
            return redirect('login_view')

        user= authenticate(username=email,password=password)
        if user is not None:
         login(request,user)
         return redirect('home')
        else:
            messages.error(request,'Invalid email or password')
            return redirect('login_view')
        
     return render(request,'accounts/login.html')





def email_view(request):
    if request.method =="POST":
        # .strip remove any kind of space tab 
        user_email= request.POST.get('email','').strip()
        # since i am storing username as a email in database
        print("Entered email from form:", repr(user_email)) 


        from django.contrib.auth.models import User
        usernames = list(User.objects.values_list('username', flat=True))
        emails = list(User.objects.values_list('email', flat=True))
        print("All usernames in DB:", usernames)
        print("All emails in DB:", emails)
        if User.objects.filter(username=user_email).exists():
            user_obj=User.objects.get(email=user_email)

            otp_num = random.randint(100000,999999)
            request.session['user_email']=user_email
            request.session['otp']= str(otp_num)

            from_email= settings.EMAIL_HOST_USER
            
            subject='Reset Your Password'
            email_form =settings.EMAIL_HOST_USER
            message=(f"Hey! {user_obj.username},\n"
                       f"Your OTP for password reset is:\n"
                       f"{otp_num}\n\n")
            send_mail(subject, message, from_email,[user_obj.email])
            return redirect('otp_view')
        else:
            messages.error(request,'User dose not exist !.Please register your account')
            return redirect('email_view')

    return render(request,'accounts/email.html')




def otp_view(request):

    if request.method =="POST":
     enterd_otp = request.POST.get('otp')
     session_otp = request.session.get('otp')

     if enterd_otp==session_otp:
         del request.session['otp']
         return redirect('resetpass_view')
     else:
         messages.error(request,'Invalid otp')
         return redirect('otp_view')
     
    return render(request,'accounts/otp.html')

def resetpass_view(request):

    email= request.session.get('user_email')
    if request.method =="POST":
        pass1= request.POST.get('pass1')
        pass2= request.POST.get('pass2')
        if pass1 == pass2:
            user= User.objects.get(email=email)
            user.set_password(pass1)
            user.save()
            messages.success(request,'Password reset sucessfully ')
        else:
            messages.error(request,'Password do not match')
            return redirect('resetpass_view')

    return render(request,'accounts/resetpass.html')


def logout_view(request):
    logout(request)
    return redirect('home')

def activate_user(request,email_token):
    try:
        profile = Profile.objects.get(email_token= email_token)
        profile.is_email_verified= True
        profile.save()

        # auto login after email verifiction
        user= profile.user
        login(request,user)
        return redirect('home')
    
    except Exception as e:
         return HttpResponse('Invalid email_token')

# to render cart template
def cart(request):
     if not request.user.is_authenticated:
          messages.error(request,'Please login to view cart !')
          return redirect('login_view')
         
     cart,created = Cart.objects.get_or_create(is_paid=False, user= request.user)
     context={
          'cart':cart,
          'quantity_range':range(1,5)
          }
     return render(request,'accounts/cart.html',context)


def buy_now(request,uid):
     product = Product.objects.get(uid=uid)
     if not request.user.is_authenticated:
          messages.error(request,'Please log in to continue !')
          return redirect('product' ,slug=product.slug)
     varient_uid = request.GET.get('varient')
     user= request.user

     cart,__ = Cart.objects.get_or_create(user= user,is_paid = False)
     size_varient = None
     if varient_uid:
            try:
                 size_varient = Size_varient.objects.filter(uid=varient_uid,product=product).first()
            except Size_varient.DoesNotExist:
                    # print('Size_varient does not exist for:', varient, product) 
                    size_varient = None

     cart_item,created = CartItems.objects.get_or_create(cart= cart, product= product,size_varient=size_varient)
    #  If the item is already in the cart, and user clicks "Buy Now" again:
    # instead of creating a duplicate, we increase the quantity of the existing item.
     if not created:
          cart_item.quantity += 1
          cart_item.save()

     # ✅ Now check for shipping address
     try:
        shipping_address = ShippingAddress.objects.get(user=user)
     except ShippingAddress.DoesNotExist:
        messages.error(request, 'Please add your shipping address before ordering.')
        return redirect('shipping_address')

#total_price = cart.get_cart_total() i can't access here total price through this because it only calculate the total price of product that store and listed in cart 
     price = product.price
     if size_varient:
        price += size_varient.price
     
     # create order
     order = Order.objects.create(
        user=user,
        shipping_address=shipping_address,
        total_price=price,
    )
     # ✅ Move only the current product into the order
     OrderItems.objects.create(
        order=order,
        product=product,
     #    quantity is on because we click a buy now button for single product 
        quantity=1,
        price=price
    )
     return redirect('checkout')
   

def add_to_cart(request,uid):
        product = Product.objects.get(uid=uid)

        if not request.user.is_authenticated:
          messages.error(request,'Please log in to continue !')
          # slug=product.slug this is done to access slug also 
          return redirect('product',slug=product.slug)
        # here varient came through get request
        varient_uid = request.GET.get('varient')
        user= request.user
        # here the card item is of user is only one untill he paid 
        cart,__ = Cart.objects.get_or_create(user= user,is_paid = False)
         

        size_varient = None
        if varient_uid:
                try:
                    size_varient = Size_varient.objects.filter(uid=varient_uid,product=product).first()
                except Size_varient.DoesNotExist:
                        # print('Size_varient does not exist for:', varient, product) 
                        size_varient = None
        
       
        cart_item,created = CartItems.objects.get_or_create(cart= cart, product= product,size_varient=size_varient)
        print("User:", request.user)
        print("Product:", product.product_name)
        print("Size:", size_varient)
        print("Cart:", cart)
        print("Created cart item?", created)

        if not created:
          cart_item.quantity += 1
          cart_item.save()
          
        if size_varient:
               cart_item.size_varient = size_varient
               cart_item.save()
               saved_item = CartItems.objects.get(pk=cart_item.pk)

        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # This line redirects the user back to the page they came from after they perform an action (like adding a product to the cart).



#  to remove cart 
def remove_cart(request,cart_item_uid):
    try:
          cart_item = CartItems.objects.get(uid= cart_item_uid)
          cart_item.delete()
    except Exception as e:
       print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
# for cart quantity
def cart_quantity(request,cart_item_uid):
     if request.method == "POST":
          cart_item = CartItems.objects.get(uid = cart_item_uid)
          quantity = int(request.POST.get('quantity',1))
          cart_item.quantity = quantity
          cart_item.save()
     return redirect('cart')
    

def profile(request):
     return render(request,'base/profile.html')


def edit_profile(request):
     user= request.user
     profile= user.profile
     if request.method == 'POST':
          first_name= request.POST.get('first_name')
          last_name= request.POST.get('last_name')
          profile_image= request.FILES.get('profile_image')

          user.first_name= first_name
          user.last_name =last_name
          user.save()

          if profile_image:
               profile.profile_image = profile_image
               profile.save()
          else:
               profile.save()
               
          return redirect('profile')
     return render(request,'accounts/edit_profile.html')


