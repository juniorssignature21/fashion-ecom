from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone

import shortuuid

PAYMENT_STATUS = (
    ("Paid","Paid"),
    ("Processing","Processing"),
    ("Failed","Failed"),
)

PAYMENT_METHOD = (
    ("Paypal","Paypal"),
    ("Stripe","Stripe"),
    ("Flutterwave","Flutterwave"),
    ("Paystack","Paystack"),
    ("RazorPay","RazorPay"),
)

ORDER_STATUS = (
    ("Pending","Pending"),
    ("Processing","Processing"),
    ("Shipped","Shipped"),
    ("Fufilled","Fufilled"),
    ("Cancelled","Cancelled"),
)

SHIPPING_SERVICE = (
    ("DHL","DHL"),
    ("FedX","FedX"),
    ("GIG Logistics","GIG Logistics"),
)

RATING = (
    (1, "⭐"),
    (2, "⭐⭐"),
    (3, "⭐⭐⭐"),
    (4, "⭐⭐⭐⭐"),
    (5, "⭐⭐⭐⭐⭐"),
)

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
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='products')
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

class Coupon(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=100)
    discount = models.IntegerField(default=1)
    
    def __str__(self):
        return self.code
    # print(f"my name is {name}")
    
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
    first_name = models.CharField(max_length=30, default="")
    last_name = models.CharField(max_length=30, default="")
    delivery_address = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=25, default="")
    email = models.EmailField(default="")  # Add email field to store user's email address
    set_as_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.delivery_address}, {self.city}, {self.state}, {self.country}"
    
    class Meta:
        verbose_name_plural = "Addresses"
        
class Order(models.Model):
    vendors = models.ManyToManyField(User, null=True, blank=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='customer', blank=True, null=True)
    sub_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    shipping = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    tax = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=100, choices=PAYMENT_STATUS, default="Processing")
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD, default=None, null=True, blank=True)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="pending")
    initial_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, null=True, blank=True, help_text="The original total before")
    saved = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, null=True,blank=True, help_text='Amount')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ManyToManyField('Coupon', blank=True, null=True)
    order_id = ShortUUIDField(length=6, max_length=25, alphabet='1234567890')
    payment_id = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Order"
        ordering = ['-date']
        
    def __str__(self):
        return f"Order {self.order_id} by {self.customer.username if self.customer else 'Unknown'}"
    
    def order_items(self):
        return OrderItem.objects.filter(order=self)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default='Pending')
    shipping_services = models.CharField(max_length=100, choices=SHIPPING_SERVICE, default=None, null=True, blank=True)
    tracking_id = models.CharField(max_length=100, default=None, null=True, blank=True)
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    color = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Grand Total of all amount")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Amount ")
    # address = models.ForeignKey("customer.Address", on_delete=models.SET_NULL, null=True)
    coupons = models.ManyToManyField(Coupon, blank=True)
    applied_coupon = models.BooleanField(default=False)
    item_id = ShortUUIDField(length=6, max_length=25, alphabet='1234567890')
    vendor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='vendor_order_items')
    date = models.DateTimeField(default=timezone.now)
    
    def order_id(self):
        
        return f"{self.order.order_id}"
    
    def __str__(self):
        return self.item_id
    
    class Meta:
        ordering = ["-date"]
        

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviews')
    review = models.TextField(null=True, blank=True)
    reply = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} review on {self.product.name}'
    