# store/context_processors.py
from .models import Cart  # Adjust this to match your Cart model
from django.db.models import Q

def cart_status(request):
    # Try to get the cartId from the cookie or session
    # Note: Since your JS uses localStorage, you might need to 
    # sync this with a session or cookie for the backend to see it on page load.
    cart_id = request.COOKIES.get('cart_id') 
    
    if cart_id:
        count = Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).count()
    else:
        count = 0
        
    return {
        'total_cart_items': count
    }
