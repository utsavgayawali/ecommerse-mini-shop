from django.shortcuts import render, redirect
from .models import ShippingAddress, Order, OrderItems
from django.contrib import messages
from accounts.models import Cart
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail


@login_required
def shipping_address(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        phone_no = request.POST.get('phone_no')
        address_line1 = request.POST.get('address_line1')
        address_line2 = request.POST.get('address_line2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zipcode')

        if all([full_name, phone_no, address_line1, city, state, zip_code]):
            ShippingAddress.objects.update_or_create(
                user=request.user,
                defaults={
                    'full_name': full_name,
                    'phone_no': phone_no,
                    'address_line1': address_line1,
                    'address_line2': address_line2,
                    'city': city,
                    'state': state,
                    'zip_code': zip_code,
                }
            )
            messages.success(request, "Shipping address saved. You can now place your order.")
            return redirect('checkout')
        else:
            messages.error(request, "All required fields must be filled!")

    # Try to fetch address safely
    address = ShippingAddress.objects.filter(user=request.user).first()

    context = {
        'shipping_address': address,
        'full_name_value': address.full_name if address else '',
        'phone_no_value': address.phone_no if address else '',
        'address_line1_value': address.address_line1 if address else '',
        'address_line2_value': address.address_line2 if address else '',
        'city_value': address.city if address else '',
        'state_value': address.state if address else '',
        'zipcode_value': address.zip_code if address else '',
    }

    return render(request, 'checkout/shipping_address.html', context)


@login_required
def checkout(request):
    address = ShippingAddress.objects.filter(user=request.user).first()
    cart = Cart.objects.filter(user=request.user, is_paid=False).first()
    return render(request, 'checkout/checkout.html', {'address': address, 'cart': cart})


@login_required
def make_purchese(request):
    user = request.user
    shipping_address = ShippingAddress.objects.filter(user=user).first()
    if not shipping_address:
        messages.error(request, 'Shipping address does not exist. Please add it before placing an order.')
        return redirect('shipping_address')

    cart = Cart.objects.filter(user=user, is_paid=False).first()
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    cart_items = cart.cart_items.all()
    if not cart_items.exists():
        messages.error(request, 'No items in your cart. Please add products before placing an order.')
        return redirect('cart')

    total_price = cart.get_cart_total()

    order = Order.objects.create(
        user=user,
        shipping_address=shipping_address,
        total_price=total_price,
    )

    for item in cart_items:
        OrderItems.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.get_product_price(),
        )

    cart.is_paid = True
    cart.save()

    subject = 'Order Confirmation'
    email_from = settings.EMAIL_HOST_USER
    message = f"Hi {user.first_name},\n\nYour order #{order.uid} has been placed successfully.\n\n"
    message += f"Total: Rs {order.total_price}\n"
    message += "Thank you for shopping with us!\n\n"
    send_mail(subject, message, email_from, recipient_list=[user.email])

    messages.success(request, 'Your order was placed successfully. Check your email for confirmation.')
    return redirect('checkout')
