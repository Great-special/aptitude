from django.contrib import admin
from .models import Category, Payment, Product, Order, OrderItem, FeedBack, AboutPageContent, NewsFeedUpdate
# Register your models here.

admin.site.register([
    Category, Payment,
    Product, Order,
    OrderItem, FeedBack,
    NewsFeedUpdate, AboutPageContent
])