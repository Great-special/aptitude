from django.urls import path
from . import views

urlpatterns = [
    path('sign-up/', views.create_user, name='sign_up'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile_page, name="profile")
]
