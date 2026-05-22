/**
 * ofazyvybez Streetwears Store Front-end Engine
 * Manages responsive layouts, AJAX cart operations, and custom WhatsApp redirections.
 */

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initProductGallery();
    initAddToCart();
    initQuantityControls();
    initCartActions();
    initCheckoutProcessor();
});

/* ==========================================================================
   NAVIGATION & OVERLAYS
   ========================================================================== */

function initNavigation() {
    const mobileNavToggle = document.getElementById('mobileNavToggle');
    const mobileNavOverlay = document.getElementById('mobileNavOverlay');
    const mobileClose = document.getElementById('mobileClose');

    if (mobileNavToggle && mobileNavOverlay) {
        mobileNavToggle.addEventListener('click', () => {
            mobileNavOverlay.classList.add('open');
        });
    }

    if (mobileClose && mobileNavOverlay) {
        mobileClose.addEventListener('click', () => {
            mobileNavOverlay.classList.remove('open');
        });
    }

    // Close mobile nav on outside click
    if (mobileNavOverlay) {
        mobileNavOverlay.addEventListener('click', (e) => {
            if (e.target === mobileNavOverlay) {
                mobileNavOverlay.classList.remove('open');
            }
        });
    }
}

/* ==========================================================================
   PRODUCT IMAGE GALLERY
   ========================================================================== */

function initProductGallery() {
    const mainImg = document.getElementById('mainProductImage');
    const thumbs = document.querySelectorAll('.img-thumb');

    if (thumbs.length > 0 && mainImg) {
        thumbs.forEach(thumb => {
            thumb.addEventListener('click', function() {
                // Remove active class from all
                thumbs.forEach(t => t.classList.remove('active'));
                // Add active to current
                this.classList.add('active');
                // Change main image source
                const newSrc = this.getAttribute('data-image-src');
                mainImg.setAttribute('src', newSrc);
            });
        });
    }
}

/* ==========================================================================
   TOAST NOTIFICATION ENGINE
   ========================================================================== */

function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    // Create toast box
    const toast = document.createElement('div');
    toast.className = `toast-box ${type}`;

    // Select icon
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'error') iconClass = 'fa-circle-exclamation';

    toast.innerHTML = `
        <i class="fa-solid ${iconClass} toast-icon"></i>
        <div class="toast-message">${message}</div>
        <i class="fa-solid fa-xmark toast-close"></i>
    `;

    // Add to container
    container.appendChild(toast);

    // Auto remove after 4.5 seconds
    const timer = setTimeout(() => {
        removeToast(toast);
    }, 4500);

    // Manual close trigger
    toast.querySelector('.toast-close').addEventListener('click', () => {
        clearTimeout(timer);
        removeToast(toast);
    });
}

function removeToast(toast) {
    toast.style.transform = 'translateX(120%)';
    toast.style.opacity = '0';
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 400);
}

// Bind to window to allow access from inline HTML files
window.showToast = showToast;

/* ==========================================================================
   AJAX CART HELPER ACTIONS
   ========================================================================== */

// Helper to acquire CSRF Token from document cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function fetchCartCount() {
    if (!window.cartUrl) return;

    fetch(window.cartUrl)
        .then(response => response.json())
        .then(data => {
            const cartCountElement = document.getElementById('cartCount');
            if (cartCountElement) {
                cartCountElement.textContent = data.total_quantity;
            }
        })
        .catch(err => console.error('Error fetching cart count:', err));
}
window.fetchCartCount = fetchCartCount;

/* ==========================================================================
   ADD TO CART ACTION
   ========================================================================== */

function initAddToCart() {
    const addToCartForm = document.getElementById('addToCartForm');
    
    if (addToCartForm) {
        addToCartForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Check variations selection validation
            const sizeChecked = document.querySelector('input[name="size"]:checked');
            const colorChecked = document.querySelector('input[name="color"]:checked');
            
            // Check if sizes or colors exist on page before enforcing
            const hasSizes = document.querySelector('input[name="size"]') !== null;
            const hasColors = document.querySelector('input[name="color"]') !== null;

            if (hasSizes && !sizeChecked) {
                showToast("Please choose a Size before adding to cart.", "error");
                return;
            }

            if (hasColors && !colorChecked) {
                showToast("Please choose a Color before adding to cart.", "error");
                return;
            }

            const productId = document.getElementById('productId').value;
            const quantity = document.getElementById('qtyInput') ? document.getElementById('qtyInput').value : 1;
            const size = sizeChecked ? sizeChecked.value : '';
            const color = colorChecked ? colorChecked.value : '';

            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', quantity);
            formData.append('size', size);
            formData.append('color', color);

            fetch(window.addToCartUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    showToast(data.message, 'success');
                    fetchCartCount(); // Update header dynamic bubble count
                } else {
                    showToast(data.message, 'error');
                }
            })
            .catch(err => {
                console.error('Error adding to cart:', err);
                showToast("Failed to add item to cart. Please try again.", "error");
            });
        });
    }
}

/* ==========================================================================
   QUANTITY INCREMENT CONTROLS
   ========================================================================== */

function initQuantityControls() {
    // Single product page quantity adjustments
    const btnMinus = document.getElementById('btnQtyMinus');
    const btnPlus = document.getElementById('btnQtyPlus');
    const qtyInput = document.getElementById('qtyInput');

    if (qtyInput) {
        if (btnMinus) {
            btnMinus.addEventListener('click', () => {
                let currentVal = parseInt(qtyInput.value) || 1;
                if (currentVal > 1) {
                    qtyInput.value = currentVal - 1;
                }
            });
        }

        if (btnPlus) {
            btnPlus.addEventListener('click', () => {
                let currentVal = parseInt(qtyInput.value) || 1;
                qtyInput.value = currentVal + 1;
            });
        }
    }
}

/* ==========================================================================
   CART PAGE ROW MODIFICATIONS
   ========================================================================== */

function initCartActions() {
    const cartItemsPanel = document.querySelector('.cart-items-panel');
    if (!cartItemsPanel) return;

    cartItemsPanel.addEventListener('click', function(e) {
        // Quantities change inside cart page
        const qtyBtn = e.target.closest('.cart-qty-btn');
        if (qtyBtn) {
            const itemKey = qtyBtn.getAttribute('data-item-key');
            const action = qtyBtn.getAttribute('data-action');
            const qtySpan = document.getElementById(`qty-${itemKey}`);
            let currentQty = parseInt(qtySpan.textContent);

            let newQty = currentQty;
            if (action === 'increase') {
                newQty = currentQty + 1;
            } else if (action === 'decrease' && currentQty > 1) {
                newQty = currentQty - 1;
            }

            if (newQty !== currentQty) {
                updateCartItemQuantity(itemKey, newQty);
            }
            return;
        }

        // Remove item from cart completely
        const removeBtn = e.target.closest('.cart-item-remove');
        if (removeBtn) {
            const itemKey = removeBtn.getAttribute('data-item-key');
            removeCartItem(itemKey);
        }
    });
}

function updateCartItemQuantity(itemKey, quantity) {
    const formData = new FormData();
    formData.append('item_key', itemKey);
    formData.append('quantity', quantity);

    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            // Update line text quantity
            const qtySpan = document.getElementById(`qty-${itemKey}`);
            if (qtySpan) qtySpan.textContent = quantity;
            
            // Update financial rows
            updateCartSummary(data);
            showToast("Cart updated successfully.", "success");
        } else {
            showToast(data.message, "error");
        }
    })
    .catch(err => {
        console.error('Error updating quantity:', err);
        showToast("Could not update quantity.", "error");
    });
}

function removeCartItem(itemKey) {
    const formData = new FormData();
    formData.append('item_key', itemKey);

    fetch('/cart/remove/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            // Slide out and destroy cart row element
            const row = document.getElementById(`row-${itemKey}`);
            if (row) {
                row.style.transform = 'translateX(-100px)';
                row.style.opacity = '0';
                setTimeout(() => {
                    row.parentNode.removeChild(row);
                    // Check if cart is now empty
                    if (document.querySelectorAll('.cart-item-row').length === 0) {
                        location.reload(); // reload to show the empty cart template state
                    }
                }, 300);
            }
            
            // Recalculate financial summary and count bubble
            updateCartSummary(data);
            fetchCartCount();
            showToast("Item removed from your cart.", "success");
        } else {
            showToast(data.message, "error");
        }
    })
    .catch(err => {
        console.error('Error removing item:', err);
        showToast("Could not remove item.", "error");
    });
}

function updateCartSummary(data) {
    // Update subtotal
    const subtotalText = document.getElementById('cartSubtotal');
    if (subtotalText) subtotalText.textContent = `₦${parseFloat(data.cart_total).toFixed(2)}`;

    // Update total
    const totalText = document.getElementById('cartTotal');
    if (totalText) totalText.textContent = `₦${parseFloat(data.cart_total).toFixed(2)}`;
}

/* ==========================================================================
   WHATSAPP CHECKOUT PROCESSOR
   ========================================================================== */

function initCheckoutProcessor() {
    const checkoutForm = document.getElementById('checkoutForm');
    if (!checkoutForm) return;

    checkoutForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const customerName = document.getElementById('customerName').value.trim();
        const customerEmail = document.getElementById('customerEmail').value.trim();
        const customerPhone = document.getElementById('customerPhone').value.trim();
        const customerAddress = document.getElementById('customerAddress').value.trim();

        if (!customerName || !customerEmail || !customerPhone || !customerAddress) {
            showToast("Please fill in all details for checkout.", "error");
            return;
        }

        const formData = new FormData();
        formData.append('customer_name', customerName);
        formData.append('customer_email', customerEmail);
        formData.append('customer_phone', customerPhone);
        formData.append('shipping_address', customerAddress);

        showToast("Processing order... Redirecting to WhatsApp", "info");

        // Submit info and create database record
        fetch('/checkout/whatsapp/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                showToast("Order registered! Launching chat...", "success");
                
                // Clear the header count bubble locally
                const cartCountElement = document.getElementById('cartCount');
                if (cartCountElement) cartCountElement.textContent = '0';
                
                // Redirect browser to encoded WhatsApp Click-to-Chat API
                setTimeout(() => {
                    window.location.href = data.whatsapp_url;
                }, 1000);
            } else {
                showToast(data.message, "error");
            }
        })
        .catch(err => {
            console.error('Checkout error:', err);
            showToast("Failed to initiate WhatsApp checkout. Try again.", "error");
        });
    });
}
