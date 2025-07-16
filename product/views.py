from django.shortcuts import render,get_object_or_404
from product.models import Product,Category
from django.db.models import Q





def product(request,slug):
  product= get_object_or_404(Product,slug=slug)
  context={'items':product}
  if request.GET.get('size'):
     size = request.GET.get('size')
     price = product.get_product_price(size)
     context['selected_size']=size
     context['updated_price']=price
  return render(request,'product/productdetail.html',context)



def product_category(request,slug):
   category = get_object_or_404(Category,slug=slug)
   products= Product.objects.filter(category=category)
   context ={
      'category':category,
      'products':products

    }
   return render(request,'product/product_category.html',context)




def search_view(request):
    query= request.GET.get('q')

    all_products=Product.objects.all()

   # here related product is the product of same category which appears after search product
    matched_products = all_products
    related_product =Product.objects.none()

    if query:
        matched_products = all_products.filter(
            Q(product_name__icontains=query)| Q(category__category_name__icontains=query)
            )
        
   # here the product which are match in search are listed
    matched_category = matched_products.values_list('category',flat=True)


   # here we exclude the matched product form allProduct in that category
    related_product = all_products.filter(
       category__in = matched_category
    ).exclude(uid__in=matched_products.values_list('uid',flat=True))
    context={
        'query':query,
        'matched_product':matched_products,
        'related_product':related_product,
    }

    return render(request,'product/search_view.html',context)