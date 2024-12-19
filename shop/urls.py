from django.urls import path
from .import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('about/', views.about_page, name='about_page'),
    path('product_page/', views.products_page, name='product_page'),
    path('contact_page/', views.contact_page, name='contact_page'),
    path('courses/', views.courses_page, name='courses_page'),
    path('cart_page/', views.cart_page, name="cart_page"),
    path('checkout/', views.check_out, name='checkout'),
    path('product/<int:id>/detail/', views.product_detail_page, name='product_detail'),
    path('product-category/<int:pk>/', views.product_category_id, name="product_category_id"),
    path('feedback/', views.get_feedback, name='get_feedback')
]

