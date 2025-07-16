from django.shortcuts import render,get_object_or_404
from product.models import Product



def home(request):
  product=Product.objects.all()
  print(f"[DEBUG] Products: {list(product)}")
  context={'items':product}
  return render(request,'home/home.html',context)

