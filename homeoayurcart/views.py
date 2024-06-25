from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from ecommerce.models import Product, Cart, CartProduct, Order, Coupon,OrderProduct
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



# Utility function to get or create a cart
from django.contrib.auth.models import User

def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        print(f"Authenticated user cart: {cart}, Created: {created}")
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_key)
        print(f"Session-based cart: {cart}, Created: {created}, Session Key: {session_key}")
    return cart

def index(request):
    products = Product.objects.all()  # Fetch all products from the database
    cart = get_cart(request)
    cart_products = CartProduct.objects.filter(cart=cart)
    
    # Debug: Print cart and cart products
    print(f"Cart: {cart}, Cart products: {cart_products}")

    context = {
        'products': products,
        'cart': cart,
        'cart_products': cart_products,
    }
    return render(request, 'index-3.html', context)


def index_2(request):
    products = Product.objects.all()  # Fetch all products from the database
    cart = get_cart(request)
    cart_products = CartProduct.objects.filter(cart=cart)
    
    context = {
        'products': products,
        'cart': cart,
        'cart_products': cart_products,
    }
    return render(request, 'index-4.html', context)

def update_cart(request):
    if request.method == 'POST':
        try:
            product_id = request.POST.get('product_id')
            action = request.POST.get('action')

            if not product_id or not action:
                return JsonResponse({'error': 'Missing product_id or action'}, status=400)

            product = get_object_or_404(Product, id=product_id)
            cart = get_cart(request)

            if action == 'add':
                cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
                if not created:
                    cart_product.quantity += 1
                    cart_product.save()
            elif action == 'remove':
                cart_product = CartProduct.objects.filter(cart=cart, product=product).first()
                if cart_product:
                    if cart_product.quantity > 1:
                        cart_product.quantity -= 1
                        cart_product.save()
                    else:
                        cart_product.delete()
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)

            cart_products = CartProduct.objects.filter(cart=cart)
            cart_data = {
                'total_items': cart_products.count(),
                'products': [{
                    'id': cp.product.id,
                    'name': cp.product.name,
                    'price': cp.product.price,
                    'image_url': cp.product.image.url  # Include the image URL
                } for cp in cart_products]
            }

            return JsonResponse(cart_data)

        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

# Utility function to get or create a cart
def get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(session_id=request.session.session_key)
    return cart
@csrf_exempt
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_cart(request)

    # Debug: Print cart information
    print(f"Adding product to cart: {product}")
    print(f"Cart details: {cart}")

    # Get or create CartProduct
    cart_product, created = CartProduct.objects.get_or_create(cart=cart, product=product)
    
    if created:
        print(f"Created new CartProduct: {cart_product}")
    else:
        cart_product.quantity += 1
        cart_product.save()
        print(f"Updated CartProduct: {cart_product}")

    # Debug: Print all cart products after addition
    all_cart_products = CartProduct.objects.filter(cart=cart)
    print(f"All cart products: {all_cart_products}")

    # Calculate total items and total price
    total_items = sum(cp.quantity for cp in all_cart_products)
    total_price = sum(cp.product.price * cp.quantity for cp in all_cart_products)

    return JsonResponse({
        'total_items': total_items,
        'total_price': total_price,
        'message': 'Product added to cart'
    })

