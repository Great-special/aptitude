# myapp/context_processors.py
from django.conf import settings
import json

def _get_cart_items(request):
    """
    Helper function to fetch and parse cart data from session.
    """
    cart_data = request.session.get(getattr(settings, 'CART_ID', 'cart'), '[]')
    try:
        return json.loads(cart_data)
    except json.JSONDecodeError:
        return []

def global_settings(request):
    """
    Context processor to add cart length to templates.
    """
    cart = _get_cart_items(request)
    
    return {
        'len_cart': len(cart)
    }
