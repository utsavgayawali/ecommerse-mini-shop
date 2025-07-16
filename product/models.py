from django.db import models
from base.models import BaseModel
from django.utils.text import slugify


class Category(BaseModel):
    category_name=models.CharField(max_length=100)
    slug = models.SlugField(null=True,blank=True)
    category_image=models.ImageField(upload_to='category')

    def save(self,*args,**kwargs):
        self.slug =slugify(self.category_name)
        super(Category,self).save(*args,**kwargs)

    def __str__(self):
        return f"{self.category_name}"


class Size_varient(BaseModel):
    size_name= models.CharField(max_length=40)
    price= models.IntegerField(default=0)
    # product= models.ForeignKey('Product',on_delete=models.CASCADE,related_name='size_varient')

    def __str__(self):
        return f"{self.size_name}"
    
class Color_varient(BaseModel):
    color_name = models.CharField(max_length=40)
    price = models.IntegerField(default=0)
    


    def __str__(self):
        return f"{self.color_name}"
    

class Product(BaseModel):
    product_name= models.CharField(max_length=40)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,related_name='product')
    price=models.IntegerField()
    slug=models.SlugField(null=True,blank=True)
    product_description=models.TextField()
    short_desc = models.CharField(max_length=50, default="")
    size_varient = models.ManyToManyField(Size_varient,blank=True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_name)
        super(Product,self).save(*args,**kwargs)

    def __str__(self):
        return f"{self.product_name}"
    
    
    def get_product_price(self,size=None):
       base_price = self.price or 0
       if size:
        size_obj= Size_varient.objects.filter(size_name=size).first()
        if size_obj and size_obj.price:
           return  base_price + size_obj.price
       return base_price
        


    
class ProductImage(BaseModel):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_image')
    image=models.ImageField(upload_to='product')



