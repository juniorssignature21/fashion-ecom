from decimal import Decimal
from pyexpat.errors import messages

from django.http import JsonResponse
from django.shortcuts import redirect, render
from store import models as store_models
from django.db.models import Q, Sum

import random
# Create your views here.
# views.py
from django.http import JsonResponse
from .models import Cart # Assuming your model name

def get_cart_count(request):
    cart_id = request.GET.get('cart_id')
    count = 0
    if cart_id:
        total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).count()
        cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else  Q(cart_id=cart_id)).aggregate(sub_total = Sum("sub_total"))["sub_total"]
        
    return JsonResponse({'total_cart_items': total_cart_items, 'cart_sub_total': f"{cart_sub_total:,.2f}"})

def HomeView(request):
    categories = store_models.Category.objects.all()[:4]
    products = store_models.Product.objects.all()[:20]
    
    context = {
        'products':products,
        'categories':categories
    }
    return render(request, 'accounts/index.html', context)

def ShopView(request):
    categories = store_models.Category.objects.all()
    products = store_models.Product.objects.all()
    
    context = {
        'products':products,
        'categories':categories
    }
    return render(request, 'store/shop.html', context)

def FilterCategory(request, foo):
    foo = foo.replace('-', ' ')
    category = store_models.Category.objects.get(name=foo or None)
    products = store_models.Product.objects.filter(category=category)
    categories = store_models.Category.objects.all()
    
    context = {
        "category":category,
        "categories":categories,
        "products":products
    }
    return render(request, "store/shop.html", context)

def ProductDetailView(request, foo):
    product = store_models.Product.objects.get(slug=foo)
    variants = store_models.Variant.objects.filter(product=product)
    related_products = store_models.Product.objects.filter(category=product.category)
    
    context = {
        "product":product,
        "variants":variants,
        "related_products":related_products
    }
    
    return render(request, "store/shop-details.html", context)

def AddToCart(request):
    id = request.GET.get("id")
    qty = request.GET.get("qty")
    size = request.GET.get("size")
    color = request.GET.get("color")
    cart_id = request.GET.get("cart_id")
    
    request.session['cart_id'] = cart_id
    
    if not id or not qty or not cart_id:
        return JsonResponse({"error":f"Missing required parameters{id},{qty},{cart_id}"}, status=400)
    try:
        products = store_models.Product.objects.get(id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error":"Product not found"}, status=404)
    
    existing_cart_items = store_models.Cart.objects.filter(cart_id=cart_id, product=products).first()
    if int(qty) > products.stock:
        return JsonResponse({"error":"Requested quantity exceeds available stock"}, status=400)
    
    if not existing_cart_items:
        cart = store_models.Cart()
        cart.product = products
        cart.price = products.price
        cart.qty = qty
        cart.size = size
        cart.color = color
        cart.sub_total = Decimal(cart.price) * Decimal(qty)
        cart.shipping = Decimal(products.shipping) * Decimal(qty)
        cart.total = cart.sub_total + cart.shipping
        cart.cart_id = cart_id
        cart.save()
        
        message = f"Added {qty} of {products.name} to cart."
        
    else:
        existing_cart_items.product = products    
        existing_cart_items.price = products.price    
        existing_cart_items.qty = qty
        existing_cart_items.color = color     
        existing_cart_items.size=  size
        existing_cart_items.sub_total = Decimal(products.price) * Decimal(qty)
        existing_cart_items.shipping = Decimal(products.shipping) * Decimal(qty)
        existing_cart_items.total = existing_cart_items.sub_total + existing_cart_items.shipping
        existing_cart_items.user = request.user if request.user.is_authenticated else None
        existing_cart_items.cart_id = cart_id
        existing_cart_items.save()
        
        message = f"Updated {products.name} in cart to {qty}."
        
    total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).count()
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).aggregate(sub_total=Sum('sub_total'))['sub_total']
    
    return JsonResponse(
        {
            "message": message,
            "total_cart_items": total_cart_items,
            "cart_sub_total": "{:,.2f}".format(cart_sub_total),
            "item_sub_total":"{:,.2f}".format(existing_cart_items.sub_total if existing_cart_items else "{:,.2f}".format(cart.sub_total)),
        })
    
def cart(request):
    if "cart_id" in request.session:
        cart_id =request.session['cart_id']
    else:
        cart_id = None
        
    items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else  Q(cart_id=cart_id))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else  Q(cart_id=cart_id)).aggregate(sub_total = Sum("sub_total"))["sub_total"]
    
    try:
        addresses = store_models.Address.objects.filter(user=request.user)
    except:
        addresses = None
        
    if not items:
        messages.warning(request, "no items in cart")
        return redirect("store:home")
    
    context = {
     "items":items,
     "addresses":addresses,   
     "cart_sub_total":f"{cart_sub_total:,.2f}" if cart_sub_total else "0.00",   
    }
    return render(request, "store/shopping-cart.html", context)

def delete_cart_item(request):
    id = request.GET.get("id")
    item_id = request.GET.get("item_id")
    cart_id = request.GET.get("cart_id")
    
    if not id and not item_id and not cart_id:
        return JsonResponse({"error": "Item or product not found"}, status=400)
    
    try:
        product  = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Product not found"}, status=404)
    
    item = store_models.Cart.objects.get(product=product, id=item_id)
    item.delete()
    
    total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).aggregate(sub_total = Sum("sub_total"))["sub_total"]
    
    return JsonResponse({
        "message": "Item deleted",
        "total_cart_items":total_cart_items.count(),
        "cart_sub_total":"{:,.2f}".format(cart_sub_total) if cart_sub_total else 0.00
    })