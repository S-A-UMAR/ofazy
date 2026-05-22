from django.urls import path
from . import views

urlpatterns = [
    # Public Storefront
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # User Session bag/cart Actions
    path('cart/', views.cart, name='cart'),
    path('cart/api/', views.cart_api, name='cart_api'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_cart, name='remove_cart'),
    
    # Direct WhatsApp checkout endpoint
    path('checkout/whatsapp/', views.checkout_whatsapp, name='checkout_whatsapp'),
    
    # Staff Admin Analytics Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/update-order/', views.update_order_status, name='update_order_status'),
    path('admin-dashboard/restock-product/', views.quick_restock, name='quick_restock'),
    
    # Auth flows
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
