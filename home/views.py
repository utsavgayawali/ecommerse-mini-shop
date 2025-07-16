from django.shortcuts import render,get_object_or_404
from product.models import Product



def home(request):
  product=Product.objects.all
  context={'items':product}
  return render(request,'home/home.html',context)

