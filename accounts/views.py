from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages
from .models import User, UserProfile


# Create your views here.

def create_user(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('user_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        newsletter = request.POST.get('newsletter', False)  # Checkbox values
        
        # Basic validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('sign_up')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('sign_up')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('sign_up')
            
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # If you have a Customer model for additional fields
            customer = UserProfile.objects.create(
                user=user,
                state=state,
                city=city,
                # pphone_number=phone_number,
                address=address,
                newsletter=newsletter
            )
            
            messages.success(request, 'Registration successful! Please login.')
            if user:
                login(request, user)
                return redirect('home_page')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('sign_up')
        
    else:
        return render(request, 'login.html')
        


def login_user(request):
    if request.method == "POST":
        email = request.POST.get('name')
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
    

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.txt'  # Plain text fallback
    html_email_template_name = 'registration/password_reset_email.html'  # HTML template
    
    
    def form_valid(self, form):
        # Call the parent method to ensure the form is processed
        response = super().form_valid(form)

        # Retrieve the email entered in the form
        email = form.cleaned_data.get('email')

        # Fetch the user associated with the email
        try:
            user = User.objects.get(email=email)
            # You can access the user's name or other attributes here
            self.extra_email_context = {
                'user_name': user.get_full_name() or user.username,  # Fallback to username if full name is not available
            }
        except User.DoesNotExist:
            # Handle case where no user is found (shouldn't happen if form validation is correct)
            self.extra_email_context = {
                'user_name': 'User',
            }

        return response
    
