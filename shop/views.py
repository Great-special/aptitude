from django.shortcuts import render,redirect,get_object_or_404
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
import json

from .models import Product,Payment,Category,Order,OrderItem, FeedBack, AboutPageContent, NewsFeedUpdate



# Create your views here.

def home_page(request):
    # Fetch all products ordered by the latest update
    products = Product.objects.all().order_by('-updated_at')
    
    # Fetch the 'courses' category only once
    courses_category = Category.objects.get(name='courses')
    
    updates = NewsFeedUpdate.objects.all().order_by('-created_at')[:2]
    
    # Context preparation
    context = {
        'products': products.exclude(category=courses_category)[:8], # Exclude 'courses'
        'new_products': products.filter(category=courses_category)[:5],  # Latest 5 products in 'courses'
        'special':products.filter(special_offer=True),
        'updates': updates,  
    }
    return render(request, 'index-2.html', context)

def about_page(request):
    about = AboutPageContent.objects.filter(current=True).first()
    context = {
        'about':about,
    }
    return render(request, 'about.html', context)

def contact_page(request):
	return render(request, 'contact.html')

def products_page(request):
    courses_category = Category.objects.get(name='courses')
    products = Product.objects.exclude(category=courses_category).order_by('-updated_at')
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
        title = 'courses'
    else:
        title = 'products'
    
    return render(request, 'single-product.html', {
        'product': product,
        'title': title,
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
		'name': product.title,
		'price': float(product.price),
		'image': product.get_image(),
		'qty': qty,
        'total_price': float(product.price) * qty,
	}

	# Update or add cart item
	existing_item = next((item for item in cart if item['id'] == str(pk)), None)
	if existing_item:
		existing_item['qty'] += qty
	else:
		cart.append(cart_item)

	request.session[settings.CART_ID] = json.dumps(cart)
	messages.success(request, f"Cart updated: Added {qty} of product {pk}")

	return redirect(referer_url)

def remove_cart(request, pk):
    cart = _get_cart_items(request)
    referer_url = request.META.get('HTTP_REFERER', '/')
    
    # Find the item in the cart
    existing_item = next((item for item in cart if item['id'] == str(pk)), None)
    
    if existing_item:
        # Check if quantity parameter is provided
        qty_to_remove = int(request.GET.get('quantity', 0))
        
        if qty_to_remove <= 0 or qty_to_remove >= existing_item['qty']:
            # Remove the entire item if qty_to_remove is 0 or greater than existing
            cart = [item for item in cart if item['id'] != str(pk)]
            messages.success(request, f"Product {pk} removed from cart")
        else:
            # Reduce the quantity and update total price
            existing_item['qty'] -= qty_to_remove
            existing_item['total_price'] = float(existing_item['price']) * existing_item['qty']
            messages.success(request, f"Cart updated: Removed {qty_to_remove} of product {pk}")
    
    # Update the session
    request.session[settings.CART_ID] = json.dumps(cart)
    
    return render(request, 'cart_row.html')

def view_cart(request):
    tab = 'cart'
    cart_items = _get_cart_items(request)
    total_price = sum(item.get('total_price', 0)  for item in cart_items)
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'tab':tab,
    })


def update_cart_qty(request, pk):
    if request.method != 'POST':
        return HttpResponse(status=405)  # Method Not Allowed

    cart = _get_cart_items(request)
    item = next((item for item in cart if item['id'] == str(pk)), None)
    operation = request.GET.get('operation')

    if not item:
        return HttpResponse(status=404)  # Item not found in cart

    # Update the quantity based on the operation
    if operation == 'increment':
        item['qty'] += 1
    elif operation == 'decrement' and item['qty'] > 1:
        item['qty'] -= 1

    # Update the total price for the item
    item['total_price'] = float(item['price']) * int(item['qty'])

    # Save the updated cart to the session
    request.session[settings.CART_ID] = json.dumps(cart)

    # Render the updated row using a partial template
    return render(request, 'cart_row.html', {'item': item})



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
        messages.success(request, f"Order processed. Total: {total_price}")
        
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