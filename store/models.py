from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation



class Product(models.Model):
    TYPE_CHOICES = [
        ('Roses', 'Roses'),
        ('Spray Roses', 'Spray Roses'),
        ('6 Roses Bqt', '6 Roses Bouquets'),
        ('1 St Rose Bqt', 'Rose Bouquets'),
        ('Bouquets 12 Stem', 'Bouquets 12 Stem'),
        ('Carnations', 'Carnations'),
        ('Mini Carnations', 'Mini Carnations'),
        ('Dianthus', 'Dianthus'),
        ('Statice', 'Statice'),
        ('Snapdragons', 'Snapdragons'),
        ('Asters', 'Asters'),
        ('Gypsophilia', 'Gypsophilia'),
        ('Lilies Oriental', 'Lilies Oriental'),
        ('Lilies L.A. Hybrid', 'Lilies L.A. Hybrid'),
        ('Hydrangeas', 'Hydrangeas'),
        ('Alstromeria', 'Alstromeria'),
        ('Hypericum', 'Hypericum'),
        ('Pom Poms', 'Pom Poms'),
        ('Mums Fuji or Cremon', 'Mums Fuji or Cremon'),
        ('Supermums', 'Supermums'),
        ('Limonium', 'Limonium'),
        ('Sinensis', 'Sinensis'),
    ]

    name = models.CharField(max_length=100)
    pack_quantity = models.CharField(max_length=50, choices=[('175','175'), ('200','200'), ('250','250'), ('120','120'), ('30','30'), ('32','32'), ('15','15'),('16','16'),('18','18'),('80','80'),('12','12'),('10','10'),('13','13'),('40','40'),('70','70'),('34','34'),('50','50'),('9','9'),('90','90'),('14','14')])
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Roses')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    color=models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    url_image=models.URLField(blank=True)
    code=models.CharField(max_length=100,default='')
    grade=models.CharField(max_length=100, blank=True, default='')
    pack_unit= models.CharField(max_length=4, choices=[('st', 'st'),('bu','bu')], blank=True, default='')

    @property
    def pack_price(self):
        if self.pack_quantity:
            try:
                return self.unit_price * Decimal(str(self.pack_quantity))
            except (InvalidOperation, TypeError):
                return None
        return None


    def __str__(self):
        return self.name
    
class FeaturedProducts(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name='featured')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_favorite')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255)
    preferred_address = models.CharField(max_length=255, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    purchase_date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('shipped', 'Shipped'), ('completed', 'Completed')], default='pending')
    delivery_address = models.CharField(max_length=500, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    stripe_session_id = models.CharField(max_length=200, blank=True, default='', db_index=True)

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
