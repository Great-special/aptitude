from django.shortcuts import render,redirect,get_object_or_404
from django.conf import settings
from django.contrib import messages
import json

from .models import Product,Payment,Category,Order,OrderItem, FeedBack



# Create your views here.

def home_page(request):
    # Fetch all products ordered by the latest update
    products = Product.objects.all().order_by('-updated_at')
    
    # Fetch the 'courses' category only once
    courses_category = Category.objects.get(name='courses')
    
    # Context preparation
    context = {
        'products': products.exclude(category=courses_category)[:8], # Exclude 'courses'
        'new_products': products.filter(category=courses_category)[:5],  # Latest 5 products in 'courses'
        'special':products.filter(special_offer=True),      
    }
    return render(request, 'index-2.html', context)

def about_page(request):
	return render(request, 'about.html')

def contact_page(request):
	return render(request, 'contact.html')

def products_page(request):
	products = Product.objects.all().order_by('-updated_at')
	context = {
	'products':products,
	}
	return render(request, 'shop.html', context)

def courses_page(request):
    # Fetch the 'courses' category only once
	courses_category = Category.objects.get(name='courses')
	products = Product.objects.filter(category=courses_category).all()
	context = {
	'courses':products,
	}
	return render(request, 'course.html', context)


def cart_page(request):
    tab = 'cart'
    cart_items = _get_cart_items(request)
    total_price = sum(item.get('qty', 0) * float(item.get('price', 0)) for item in cart_items)
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'tab':tab,
    })

def product_detail_page(request, id):
    product = get_object_or_404(Product, pk=id)
    if product.category == Category.objects.get(name='courses'):
        template_name = 'course.html'
    else:
        template_name = 'shop.html'
    
    return render(request, template_name, {
        'product': product,
    })

def product_category_id(request, pk):
    category = get_object_or_404(Category, pk=pk)    
    return render(request, 'collection-list.html', {
        'products': category.products.all(),
    })

def category_detail(request, pk):
	category = get_object_or_404(Category, pk=pk) 
	products = Product.objects.filter(category=category) 
	return render(request, 'category-detail.html',{'category':category,'products':products})

def get_feedback(request):
    if request.POST:
        name = request.POST.get('con_name', '')
        email = request.POST.get('con_email', '')
        subject = request.POST.get('con_subject', '')
        phone = request.POST.get('con_phone', '')
        message = request.POST.get('con_message', '')
        
        FeedBack.objects.create(name=name, email=email, subject=subject, phone=phone, message=message)
        
    return redirect('home_page')

def add_cart(request, pk):
	qty = int(request.GET.get('quantity', 1))
	cart = _get_cart_items(request)
	product = get_object_or_404(Product, pk=pk)
	referer_url = request.META.get('HTTP_REFERER', '/')

	cart_item = {
		'id': str(pk),
		'name': product.name,
		'price': float(product.price),
		'image': product.get_image(),
		'qty': qty
	}

	# Update or add cart item
	existing_item = next((item for item in cart if item['id'] == str(pk)), None)
	if existing_item:
		existing_item['qty'] += qty
	else:
		cart.append(cart_item)

	request.session[settings.CART_ID] = json.dumps(cart)
	messages.success(f"Cart updated: Added {qty} of product {pk}")

	return redirect(referer_url)

def view_cart(request):
    tab = 'cart'
    cart_items = _get_cart_items(request)
    total_price = sum(item.get('qty', 0) * float(item.get('price', 0)) for item in cart_items)
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'tab':tab,
    })



def check_out(request):
    tab = 'check_out'
    cart = _get_cart_items(request)
    total_price = sum(int(item.get('qty', 0)) * float(item.get('price', 0)) for item in cart)
    if request.method == "POST":
        # Basic validation
        if not cart:
            messages.error(request, "Your cart is empty")
            return redirect('view_cart')
        
        # Create an order in the database
        order = Order.objects.create(user=request.user, total_price=total_price)
        for item in cart:
            product = Product.objects.get(id=item.get('id'))
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['qty'],
                price=product.price,
            )
            # removing the sold items
            product.quantity -= item['qty']
            product.save()

        # Clear the cart
        cart.clear()
        
        # Clear cart after order processing
        request.session[settings.CART_ID] = json.dumps([])
        messages.success(f"Order processed. Total: {total_price}")
        
        # Redirect to Paystack payment page
        # return render(request, 'paystack_payment.html', {
        #     'order': order,
        #     'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
        #     'total_price': total_price,
        # })
        
        return redirect('home_page')
    
    return render(request, 'cart.html', {
        'cart_items': cart,
        'total_price': total_price,
        'tab':tab,
    })


def to_wish_list(request, pk):
    wishlist = _get_wishlist(request)
    product = get_object_or_404(Product, pk=pk)
    
    # Convert to strings for comparison
    product_id = str(pk)
    
    if any(item['id'] == product_id for item in wishlist):
        wishlist = [item for item in wishlist if item['id'] != product_id]
    else:
        wishlist.append({
            'id': product_id,
            'name': product.name,
            'price': float(product.price),
            'image': product.get_image()
        })
    
    request.session[settings.WISH_ID] = json.dumps(wishlist)
    return redirect(request.META.get('HTTP_REFERER', '/'))

def view_wish_list(request):
    tab = 'wish_list'
    wishlist = _get_wishlist(request)
    cart = _get_cart_items(request)
    
    
    return render(request, 'cart.html', {
        'wish_list': wishlist,
        'cart_items': cart,
        'tab':tab,
    })


def _get_cart_items(request):
    cart_data = request.session.get(settings.CART_ID, '[]')
    try:
        return json.loads(cart_data)
    except json.JSONDecodeError:
        return []

def _get_wishlist(request):
    wishlist_data = request.session.get(settings.WISH_ID, '[]')
    try:
        return json.loads(wishlist_data)
    except json.JSONDecodeError:
        return []