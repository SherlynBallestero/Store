from django.urls import path
from .views import (
    login_view, index, register, add_to_cart, cart_view, catalog_view, product_detail_view,
    logout_view, contact_view, profile_view, toggle_favorite,
    checkout_view, stripe_success_view, confirmation_view,
)
from django.views.generic import TemplateView

urlpatterns = [
  
    path('', index, name='home'),
    
    # Catalog
    path('catalog/', catalog_view, name='catalog'),
    
    # Product Details
    path('product/<int:pk>/', product_detail_view, name='product_detail'),
    path('favorites/toggle/<int:pk>/', toggle_favorite, name='toggle_favorite'),
    
    # Cart and Checkout
    path('cart/', cart_view, name='cart'),
    path('add-to-cart/<int:pk>/', add_to_cart, name='add_to_cart'),  # Uncommented; define add_to_cart in views.py if not already
    path('checkout/', checkout_view, name='checkout'),
    path('checkout/success/', stripe_success_view, name='checkout_success'),
    path('confirmation/<int:pk>/', confirmation_view, name='confirmation'),
    
    # Auth
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Profile
    path('profile/', profile_view, name='profile'),
    
    # About and Contact (Placeholders)
    path('about/', TemplateView.as_view(template_name='store/about.html'), name='about'),
    path('contact/', contact_view, name='contact'),
]