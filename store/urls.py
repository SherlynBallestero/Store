from django.urls import path
from .views import (
    login_view, index, register, add_to_cart, cart_view, catalog_view, product_detail_view, logout_view, contact_view  # Add more views here as you define them (e.g., add_to_cart)
)
from django.views.generic import TemplateView  # For placeholders

urlpatterns = [
  
    path('', index, name='home'),
    
    # Catalog
    path('catalog/', catalog_view, name='catalog'),
    
    # Product Details
    path('product/<int:pk>/', product_detail_view, name='product_detail'),
    
    # Cart and Checkout
    path('cart/', cart_view, name='cart'),
    path('add-to-cart/<int:pk>/', add_to_cart, name='add_to_cart'),  # Uncommented; define add_to_cart in views.py if not already
    path('checkout/', TemplateView.as_view(template_name='store/checkout.html'), name='checkout'),
    path('confirmation/<int:pk>/', TemplateView.as_view(template_name='store/confirmation.html'), name='confirmation'),
    
    # Auth
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Profile (Placeholder)
    path('profile/', TemplateView.as_view(template_name='store/profile.html'), name='profile'),
    
    # About and Contact (Placeholders)
    path('about/', TemplateView.as_view(template_name='store/about.html'), name='about'),
    path('contact/', contact_view, name='contact'),
]