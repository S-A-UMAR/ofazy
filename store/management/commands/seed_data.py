from django.core.management.base import BaseCommand
from store.models import Category, Product
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Seeds mock streetwear categories and products'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Categories
        categories_data = [
            {
                'name': 'Sneakers',
                'description': 'Premium kicks, retro lows, and streetwear runners.',
                'image_url': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?q=80&w=600&auto=format&fit=crop'
            },
            {
                'name': 'Shirts',
                'description': 'Heavyweight box tees, raw-cut designs, and graphic shirts.',
                'image_url': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?q=80&w=600&auto=format&fit=crop'
            },
            {
                'name': 'Loafers',
                'description': 'Handcrafted premium suede loafers with custom stitching.',
                'image_url': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?q=80&w=600&auto=format&fit=crop'
            },
            {
                'name': 'Polos',
                'description': 'Knit collared polos with sleek minimalist aesthetics.',
                'image_url': 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?q=80&w=600&auto=format&fit=crop'
            },
            {
                'name': 'Jeans',
                'description': 'Double-knee cargo denim, washed finishes, and relaxed silhouettes.',
                'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?q=80&w=600&auto=format&fit=crop'
            },
            {
                'name': 'Slides',
                'description': 'Ergonomic cloud foam slides for recovery and leisure.',
                'image_url': 'https://images.unsplash.com/photo-1603252109303-2751441dd157?q=80&w=600&auto=format&fit=crop'
            },
            {
                'name': 'Accessories',
                'description': 'Canvas utility totes, heavyweight beanies, and modern caps.',
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?q=80&w=600&auto=format&fit=crop'
            }
        ]

        categories = {}
        for cat in categories_data:
            obj, created = Category.objects.get_or_create(
                slug=slugify(cat['name']),
                defaults={
                    'name': cat['name'],
                    'description': cat['description'],
                    'image_url_link': cat['image_url']
                }
            )
            categories[cat['name']] = obj
            if created:
                self.stdout.write(f"Created category: {cat['name']}")

        # 2. Products
        products_data = [
            # Sneakers
            {
                'category': categories['Sneakers'],
                'name': 'Streetwear Retro Low "Vapor Orange"',
                'description': 'The signature ofazyvybez sneaker. Crafted with full-grain leather, premium nubuck overlays in vapor orange, and a cream-white midsole. Embellished with streetwear branding on the tongue.',
                'price': 165.00,
                'stock': 24,
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=600&auto=format&fit=crop',
                'is_featured': True,
                'color_variants': 'Vapor Orange, Charcoal Grey, Ice White',
                'size_variants': 'US 8, US 9, US 10, US 11, US 12'
            },
            {
                'category': categories['Sneakers'],
                'name': 'Phantom Mesh Runner',
                'description': 'Super-breathable ripstop mesh construction with reflective overlays and responsive performance soles. Ideal for late-night city streets.',
                'price': 180.00,
                'stock': 12,
                'image_url': 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?q=80&w=600&auto=format&fit=crop',
                'is_featured': True,
                'color_variants': 'Midnight Black, Neon Green, Silver Chrome',
                'size_variants': 'US 8, US 9, US 10, US 11'
            },
            
            # Shirts
            {
                'category': categories['Shirts'],
                'name': 'Velocity Heavyweight Box Tee',
                'description': 'Cut from massive 300GSM premium dry cotton. Features our custom graphic chest branding with a slightly oversized fit and thick ribbing.',
                'price': 48.00,
                'stock': 45,
                'image_url': 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?q=80&w=600&auto=format&fit=crop',
                'is_featured': True,
                'color_variants': 'Sand Beige, Vintage Black, Off-White',
                'size_variants': 'S, M, L, XL'
            },
            {
                'category': categories['Shirts'],
                'name': 'Streetwear Oversized Hoodie',
                'description': 'Heavy fleece-back French terry, custom double-lined hood, and minimalist front puff-print. Perfect layer for cooler evenings.',
                'price': 95.00,
                'stock': 18,
                'image_url': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?q=80&w=600&auto=format&fit=crop',
                'is_featured': False,
                'color_variants': 'Charcoal Grey, Forest Green, Black',
                'size_variants': 'M, L, XL'
            },

            # Loafers
            {
                'category': categories['Loafers'],
                'name': 'Atelier Split-Toe Suede Loafer',
                'description': 'Handcrafted suede loafer featuring double-stitching details, visual brass buckle ornament, and flexible crepe soles. Elevating the casual look to runway standard.',
                'price': 210.00,
                'stock': 8,
                'image_url': 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?q=80&w=600&auto=format&fit=crop',
                'is_featured': True,
                'color_variants': 'Camel Suede, Navy Blue, Onyx Black',
                'size_variants': 'US 8, US 9, US 10, US 11'
            },

            # Polos
            {
                'category': categories['Polos'],
                'name': 'Classique Knit Cable Polo',
                'description': 'A breathable vintage-style cable knit polo shirt with soft collars and ribbed hems. Provides that modern prep-street aesthetic.',
                'price': 65.00,
                'stock': 15,
                'image_url': 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?q=80&w=600&auto=format&fit=crop',
                'is_featured': False,
                'color_variants': 'Cream White, Olive Green, Sky Blue',
                'size_variants': 'S, M, L, XL'
            },

            # Jeans
            {
                'category': categories['Jeans'],
                'name': 'Washed Double-Knee Cargo Denim',
                'description': 'Heavily washed 14oz ring-spun denim with utility side cargo panels and reinforced double knees. Engineered for supreme durability.',
                'price': 110.00,
                'stock': 20,
                'image_url': 'https://images.unsplash.com/photo-1542272604-787c3835535d?q=80&w=600&auto=format&fit=crop',
                'is_featured': True,
                'color_variants': 'Acid Indigo, Stonewash Grey',
                'size_variants': '30, 32, 34, 36'
            },

            # Slides
            {
                'category': categories['Slides'],
                'name': 'Cloud Foam Recovery Slides',
                'description': 'Injection-molded EVA construction for ergonomic, high-density comfort. Non-slip traction and wide upper footband styling.',
                'price': 40.00,
                'stock': 30,
                'image_url': 'https://images.unsplash.com/photo-1603252109303-2751441dd157?q=80&w=600&auto=format&fit=crop',
                'is_featured': False,
                'color_variants': 'Bone Beige, Slate Black, Tangerine',
                'size_variants': 'US 7, US 8, US 9, US 10, US 11'
            },

            # Accessories
            {
                'category': categories['Accessories'],
                'name': 'Streetwear Heavy Duty Utility Tote',
                'description': '16oz military cotton canvas tote featuring high-density nylon carry straps, dual utility side pockets, and metal hardware. Large capacity for streetwear hauls.',
                'price': 45.00,
                'stock': 25,
                'image_url': 'https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600&auto=format&fit=crop',
                'is_featured': False,
                'color_variants': 'Off-White Canvas, Stealth Black',
                'size_variants': 'One Size'
            },
            {
                'category': categories['Accessories'],
                'name': 'Vandal Heavy Ribbed Beanie',
                'description': 'Premium chunky acrylic rib-knit beanie with double cuff fold and woven brand tag. Keep warm without losing your edge.',
                'price': 25.00,
                'stock': 50,
                'image_url': 'https://images.unsplash.com/photo-1576871337622-98d48d4aa53e?q=80&w=600&auto=format&fit=crop',
                'is_featured': False,
                'color_variants': 'Vandal Orange, Charcoal Black, Sand',
                'size_variants': 'One Size'
            }
        ]

        for prod in products_data:
            obj, created = Product.objects.get_or_create(
                slug=slugify(prod['name']),
                defaults={
                    'category': prod['category'],
                    'name': prod['name'],
                    'description': prod['description'],
                    'price': prod['price'],
                    'stock': prod['stock'],
                    'image_url_link': prod['image_url'],
                    'is_featured': prod['is_featured'],
                    'color_variants': prod['color_variants'],
                    'size_variants': prod['size_variants']
                }
            )
            if created:
                self.stdout.write(f"Created product: {prod['name']}")

        self.stdout.write("Database successfully seeded with streetwear mock data!")
