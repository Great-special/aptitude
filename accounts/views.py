from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .models import User, UserProfile


# Create your views here.

def create_user(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone-number')
        password = request.POST.get('password')
        
        user = User.objects.create_user(username=email, email=email, password=password, first_name=name)
        UserProfile.objects.create(user=user, phone_number=phone_number)
        if user:
            login(request, user)
            return redirect('home_page')
    else:
        return render(request, 'login.html')
        


def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_obj = get_object_or_404(User, email=email) 
        except:
            user_obj = get_object_or_404(User, username=email)
        
        user = authenticate(request, username=user_obj.username, password=password)
        
        if user:
            login(request, user)
            return redirect('home_page')
    else:
        return render(request, 'login.html')



def logout_user(request):
    logout(request)
    return redirect('login')



def profile_page(request):
    user = request.user
    return render(request, 'my-account.html', {'user':user})
    
    