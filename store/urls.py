from django.urls import path
from store import views as store_views

app_name = "store"

urlpatterns = [
    path('', store_views.HomeView, name="home"),
    path('shop/', store_views.ShopView, name="shop"),
    path('shop/<str:foo>/', store_views.FilterCategory, name="filter_products"),
    path('shop/detail/<str:foo>/', store_views.ProductDetailView, name="product_detail"),
    # ================ cart urls
    path('add-to-cart/', store_views.AddToCart, name="add-to-cart"),
    path('cart/', store_views.cart, name="cart"),
    path('delete-cart-item/', store_views.delete_cart_item, name="delete-cart-item"),
    path('get-cart-count/', store_views.get_cart_count, name='get_cart_count'),
    path('create-order/', store_views.CreateOrder, name="create_order"),
    path('checkout/<int:id>/', store_views.checkout, name="checkout"),
    

]
