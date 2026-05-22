from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image_url = models.CharField(max_length=500, blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    # Comma-separated options, e.g., "Black,White,Orange"
    color_variants = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated colors")
    # Comma-separated options, e.g., "S,M,L,XL" or "8,9,10,11"
    size_variants = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated sizes")

    def get_color_list(self):
        if self.color_variants:
            return [x.strip() for x in self.color_variants.split(',') if x.strip()]
        return []

    def get_size_list(self):
        if self.size_variants:
            return [x.strip() for x in self.size_variants.split(',') if x.strip()]
        return []

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    whatsapp_sent = models.BooleanField(default=False)
    shipping_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # price snapshot at time of purchase
    
    # Store variations selected at checkout
    selected_color = models.CharField(max_length=50, blank=True, null=True)
    selected_size = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'} ({self.selected_size}/{self.selected_color})"
