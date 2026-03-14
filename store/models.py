from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User



class Product(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=[('flower', 'Flower'), ('floral_arrangement', 'Floral Arrangement'), ('gift', 'Gift')])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    color=models.CharField(max_length=100)
    available_quantity = models.PositiveIntegerField(default=0)
    url_image=models.URLField(blank=True)
    code=models.CharField(max_length=100,default='1AFD')
    grade=models.CharField(max_length=100, blank=True, default='')
    pack_quantity=models.PositiveIntegerField(null=True, blank=True)
    pack_unit= models.CharField(max_length=4, choices=[('st', 'st'),('bu','bu')], blank=True, default='')

    @property
    def pack_price(self):
        if self.pack_quantity:
            return self.unit_price * self.pack_quantity
        return None

    def clean(self):
        errors = {}

        if self.type == 'flower':
            if not self.grade:
                errors['grade'] = 'Grade is required for flower products.'
            if not self.pack_quantity:
                errors['pack_quantity'] = 'Pack quantity is required for flower products.'
            if not self.pack_unit:
                errors['pack_unit'] = 'Pack unit is required for flower products.'
        else:
            # For non-flower products these fields should stay empty.
            self.grade = ''
            self.pack_quantity = None
            self.pack_unit = ''

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class FeaturedProducts(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name='featured')


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    purchase_date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('completed', 'Completed')], default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"

    def calculate_total(self):
        self.total = sum(item.subtotal() for item in self.orderdetail_set.all())
        self.save()
#to manage relation orders and products(in a order there are multiples order details(product-quantity))
class OrderDetail(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase.

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def subtotal(self):
        return self.quantity * self.price
