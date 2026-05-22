import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from .models import Category, Product, Order, OrderItem

# ==========================================================================
# PUBLIC PAGES
# ==========================================================================

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_featured=True)[:4]
    new_drops = Product.objects.order_by('-id')[:4]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_drops': new_drops
    }
    return render(request, 'store/home.html', context)


def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    
    # 1. Search filter
    search_query = request.GET.get('search', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        
    # 2. Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    # 3. Size filter
    size_filter = request.GET.get('size', '')
    if size_filter:
        products = products.filter(size_variants__icontains=size_filter)
        
    # 4. Color filter
    color_filter = request.GET.get('color', '')
    if color_filter:
        products = products.filter(color_variants__icontains=color_filter)
        
    # 5. Price filter
    price_max = request.GET.get('price_max', '')
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass

    # 6. Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-id')
        
    # Extract unique filter parameters in seeded inventory
    all_sizes = ['S', 'M', 'L', 'XL', 'US 7', 'US 8', 'US 9', 'US 10', 'US 11', 'US 12', '30', '32', '34', '36']
    all_colors = ['Vapor Orange', 'Charcoal Grey', 'Ice White', 'Midnight Black', 'Sand Beige', 'Off-White', 'Camel Suede', 'Stealth Black']

    context = {
        'products': products,
        'categories': categories,
        'all_sizes': all_sizes,
        'all_colors': all_colors,
        'selected_category': category_slug,
        'selected_size': size_filter,
        'selected_color': color_filter,
        'selected_sort': sort_by,
        'search_query': search_query,
        'product_count': products.count()
    }
    return render(request, 'store/shop.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'store/product.html', context)


def about(request):
    return render(request, 'store/about.html')


def contact(request):
    return render(request, 'store/contact.html')



# ==========================================================================
# AUTHENTICATION
# ==========================================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # If user is staff, redirect directly to dashboard
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('home')
    else:
        form = AuthenticationForm()
        
    return render(request, 'store/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
        
    return render(request, 'store/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# ==========================================================================
# SESSION CART PAGES & API
# ==========================================================================

def cart(request):
    session_cart = request.session.get('cart', {})
    cart_items = []
    cart_total = 0.0
    
    for item_key, item in session_cart.items():
        subtotal = float(item['price']) * int(item['quantity'])
        cart_total += subtotal
        
        # Load actual product db object to verify image/stock
        product = Product.objects.filter(id=item['product_id']).first()
        
        cart_items.append({
            'key': item_key,
            'product': product,
            'product_id': item['product_id'],
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'size': item['size'],
            'color': item['color'],
            'subtotal': subtotal
        })
        
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total
    }
    return render(request, 'store/cart.html', context)


def cart_api(request):
    session_cart = request.session.get('cart', {})
    total_quantity = sum(int(item['quantity']) for item in session_cart.values())
    cart_total = sum(float(item['price']) * int(item['quantity']) for item in session_cart.values())
    
    return JsonResponse({
        'total_quantity': total_quantity,
        'cart_total': cart_total
    })


def add_to_cart(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    size = request.POST.get('size', '')
    color = request.POST.get('color', '')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Simple stock verification
    if product.stock <= 0:
        return JsonResponse({'status': 'error', 'message': 'Product is out of stock.'})
    if quantity > product.stock:
         return JsonResponse({'status': 'error', 'message': f'Only {product.stock} items left in inventory.'})

    # Unique identifier key for variations combinations
    item_key = f"{product_id}_{size}_{color}"
    
    # Get or init cart session
    session_cart = request.session.get('cart', {})
    
    if item_key in session_cart:
        new_qty = session_cart[item_key]['quantity'] + quantity
        if new_qty > product.stock:
            return JsonResponse({'status': 'error', 'message': f'Cannot exceed available stock ({product.stock}).'})
        session_cart[item_key]['quantity'] = new_qty
    else:
        session_cart[item_key] = {
            'product_id': product.id,
            'name': product.name,
            'price': str(product.price),
            'quantity': quantity,
            'size': size,
            'color': color
        }
        
    request.session['cart'] = session_cart
    request.session.modified = True
    
    return JsonResponse({
        'status': 'success',
        'message': f'Added {product.name} ({size}/{color}) to your bag.'
    })


def update_cart(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    item_key = request.POST.get('item_key')
    quantity = int(request.POST.get('quantity', 1))
    
    session_cart = request.session.get('cart', {})
    
    if item_key in session_cart:
        product_id = session_cart[item_key]['product_id']
        product = get_object_or_404(Product, id=product_id)
        
        if quantity > product.stock:
            return JsonResponse({'status': 'error', 'message': f'Requested quantity exceeds stock ({product.stock}).'})
            
        session_cart[item_key]['quantity'] = quantity
        request.session['cart'] = session_cart
        request.session.modified = True
        
        cart_total = sum(float(item['price']) * int(item['quantity']) for item in session_cart.values())
        
        return JsonResponse({
            'status': 'success',
            'cart_total': cart_total
        })
        
    return JsonResponse({'status': 'error', 'message': 'Item not found in cart.'})


def remove_cart(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    item_key = request.POST.get('item_key')
    session_cart = request.session.get('cart', {})
    
    if item_key in session_cart:
        del session_cart[item_key]
        request.session['cart'] = session_cart
        request.session.modified = True
        
        cart_total = sum(float(item['price']) * int(item['quantity']) for item in session_cart.values())
        
        return JsonResponse({
            'status': 'success',
            'cart_total': cart_total
        })
        
    return JsonResponse({'status': 'error', 'message': 'Item not found in cart.'})


# ==========================================================================
# WHATSAPP CHECKOUT LOGIC
# ==========================================================================

def checkout_whatsapp(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    session_cart = request.session.get('cart', {})
    if not session_cart:
        return JsonResponse({'status': 'error', 'message': 'Cart is empty.'})
        
    customer_name = request.POST.get('customer_name')
    customer_email = request.POST.get('customer_email')
    customer_phone = request.POST.get('customer_phone')
    shipping_address = request.POST.get('shipping_address')
    
    if not customer_name or not customer_email or not customer_phone or not shipping_address:
        return JsonResponse({'status': 'error', 'message': 'Missing customer details or shipping address.'})
        
    # Calculate order total
    total_price = sum(float(item['price']) * int(item['quantity']) for item in session_cart.values())
    
    # 1. Register order in database
    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        shipping_address=shipping_address,
        total_price=total_price,
        status='Pending'
    )
    
    # 2. Add line items to order and deduct stock!
    message_items = []
    for item_key, item in session_cart.items():
        product = Product.objects.filter(id=item['product_id']).first()
        qty = int(item['quantity'])
        
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            price=float(item['price']),
            selected_size=item['size'],
            selected_color=item['color']
        )
        
        # Deduct stock
        if product:
            product.stock = max(0, product.stock - qty)
            product.save()
            
        # Format string for WhatsApp message
        variation_str = f" ({item['size']}/{item['color']})" if (item['size'] or item['color']) else ""
        message_items.append(f"- {qty}x {item['name']}{variation_str} @ ₦{item['price']}")
        
    # 3. Create the pre-filled URLencoded WhatsApp click-to-chat API string
    store_whatsapp_number = "+2348131695735" # Store WhatsApp business number
    
    message_body = (
        f"🚨 *NEW STREETWEAR DROP ORDER #{order.id}*\n\n"
        f"👤 *Customer details:*\n"
        f"Name: {customer_name}\n"
        f"Email: {customer_email}\n"
        f"Phone: {customer_phone}\n"
        f"📍 *Shipping Address:* {shipping_address}\n\n"
        f"📦 *Items ordered:*\n"
        f"{chr(10).join(message_items)}\n\n"
        f"💰 *Total amount:* ₦{total_price:.2f}\n\n"
        f"Please confirm my order and send shipping details! ⚡️"
    )
    
    encoded_message = urllib.parse.quote(message_body)
    whatsapp_url = f"https://api.whatsapp.com/send?phone={store_whatsapp_number}&text={encoded_message}"
    
    # Set Order whatsapp_sent = True since URL is compiled
    order.whatsapp_sent = True
    order.save()
    
    # 4. Clear the shopping cart session
    request.session['cart'] = {}
    request.session.modified = True
    
    return JsonResponse({
        'status': 'success',
        'whatsapp_url': whatsapp_url
    })


# ==========================================================================
# STAFF ADMIN ANALYTICS DASHBOARD
# ==========================================================================

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # 1. Financial totals
    orders = Order.objects.all().order_by('-id')
    total_sales = Order.objects.filter(status='Delivered').aggregate(Sum('total_price'))['total_price__sum'] or 0.00
    pending_sales = Order.objects.filter(status='Pending').aggregate(Sum('total_price'))['total_price__sum'] or 0.00
    
    # 2. Counter logs
    total_orders_count = orders.count()
    pending_orders_count = Order.objects.filter(status='Pending').count()
    out_of_stock_products_count = Product.objects.filter(stock=0).count()
    active_customers_count = Order.objects.values('customer_email').distinct().count()
    
    # 3. Category distribution
    categories = Category.objects.annotate(product_count=Count('products'))
    
    # 4. Stock alert logs
    low_stock_products = Product.objects.filter(stock__lte=5).order_by('stock')
    
    # 5. Orders breakdown
    order_items_qty = OrderItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Analytics graph helpers (order status count)
    status_counts = Order.objects.values('status').annotate(count=Count('id'))
    status_dict = {'Pending': 0, 'Confirmed': 0, 'Shipped': 0, 'Delivered': 0}
    for item in status_counts:
        if item['status'] in status_dict:
            status_dict[item['status']] = item['count']

    # Popular Products calculations
    popular_products = Product.objects.annotate(
        sales_qty=Sum('order_items__quantity')
    ).filter(sales_qty__gt=0).order_by('-sales_qty')[:5]

    context = {
        'orders': orders[:10], # Show top 10 recent orders
        'total_sales': total_sales,
        'pending_sales': pending_sales,
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'out_of_stock_products_count': out_of_stock_products_count,
        'active_customers_count': active_customers_count,
        'categories': categories,
        'low_stock_products': low_stock_products,
        'status_dict': status_dict,
        'popular_products': popular_products,
        'order_items_qty': order_items_qty
    }
    return render(request, 'store/admin_dashboard.html', context)


@user_passes_test(lambda u: u.is_staff)
def update_order_status(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    order_id = request.POST.get('order_id')
    new_status = request.POST.get('status')
    
    order = get_object_or_404(Order, id=order_id)
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        return JsonResponse({
            'status': 'success',
            'message': f'Order #{order.id} status successfully updated to {new_status}.'
        })
        
    return JsonResponse({'status': 'error', 'message': 'Invalid status.'})


@user_passes_test(lambda u: u.is_staff)
def quick_restock(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    product_id = request.POST.get('product_id')
    amount = int(request.POST.get('amount', 10))
    
    product = get_object_or_404(Product, id=product_id)
    product.stock += amount
    product.save()
    
    return JsonResponse({
        'status': 'success',
        'message': f'Added {amount} items to {product.name}. New stock: {product.stock}',
        'new_stock': product.stock
    })
