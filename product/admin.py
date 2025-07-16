from django.contrib import admin
from .models import Category, Product,ProductImage,Size_varient,Color_varient


admin.site.register(Category)
#  here we have add the ProductImage models inside the Product so we can edit images directly in product 
class ProductImageAdmin(admin.StackedInline): 
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list= ['product_name','price']
    inlines =[ProductImageAdmin]


# registering through class id more recommended when we created a admin custom classes
@admin.register(Size_varient)
class Size_varientAdmin(admin.ModelAdmin):
    list= ['size_name','price']
    model = Size_varient

@admin.register(Color_varient)
class Color_varientAdmin(admin.ModelAdmin):
    list= ['color_name','price']
    model = Color_varient



admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage)
