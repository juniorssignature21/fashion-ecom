from django.contrib import admin
from .models import Category, Product, ProductImage, Variant, VariantOption, Tag, Cart, Address

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']
    
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(Variant)
admin.site.register(VariantOption)
admin.site.register(Tag)

class CartAdmin(admin.ModelAdmin):
    list_display = ['cart_id', 'product', 'user', 'qty', 'size', 'color', 'date']
    
admin.site.register(Cart, CartAdmin)

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']
    
admin.site.register(Address, AddressAdmin)