from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.image_url)
        return "No Image"
    image_preview.short_description = 'Image'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'category', 'price', 'stock', 'is_featured')
    list_filter = ('category', 'is_featured')
    list_editable = ('price', 'stock', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 4px;" />', obj.image_url)
        return "No Image"
    image_preview.short_description = 'Image'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'customer_phone', 'status', 'total_price', 'created_at', 'whatsapp_sent')
    list_filter = ('status', 'whatsapp_sent', 'created_at')
    list_editable = ('status',)
    search_fields = ('customer_name', 'customer_email', 'customer_phone', 'id')
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'selected_size', 'selected_color')
    list_filter = ('selected_size', 'selected_color')
    search_fields = ('product__name', 'order__customer_name')

