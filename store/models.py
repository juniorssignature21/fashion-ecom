from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify
from django.contrib.auth import get_user_model

import shortuuid

User = get_user_model()
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.name
    def product_count(self):
        return Product.objects.filter(category=self).count()
    class Meta:
        verbose_name_plural = "Categories"
    
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    stock = models.PositiveIntegerField()
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sku = ShortUUIDField(length=5, prefix='SKU-', unique=True, editable=False, alphabet='0123456789')
    slug = models.SlugField(null=True, blank=True, unique=True)
    is_sale = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + '-' + shortuuid.uuid().lower()[:2]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def image(self):
        image = ProductImage.objects.filter(product=self).first()
        return image.image.url if image else None
    
    def product_images(self):
        return ProductImage.objects.filter(product=self)
    
    def variants(self):
        return Variant.objects.filter(product=self)
    
    def prod_tags(self):
        return Tag.objects.filter(product=self)
        
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

    def items(self):
        return VariantOption.objects.filter(variant=self)
    
class VariantOption(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
class Tag(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    
    def __str__(self):
        return self.title

    
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.PositiveIntegerField(default=0, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True,blank=True)
    sub_total = models.DecimalField(decimal_places=2,max_digits=12, default=0.00, null=True, blank=True)
    shipping = models.DecimalField(decimal_places=2,max_digits=12, default=0.00, null=True, blank=True)
    tax = models.DecimalField(decimal_places=2,max_digits=12, default=0.00, null=True, blank=True)
    total = models.DecimalField(decimal_places=2,max_digits=12, default=0.00, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    cart_id = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.cart_id} - {self.product.name} - {self.qty}'
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.address_line1}, {self.city}, {self.state}, {self.country}"