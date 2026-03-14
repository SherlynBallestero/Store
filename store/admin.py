# Register your models here.
from django.contrib import admin
from .models import Product, Order, OrderDetail, Customer, FeaturedProducts


# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Customer)
admin.site.register(FeaturedProducts)