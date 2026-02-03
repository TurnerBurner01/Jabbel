from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import auth

# Get the User model
User = get_user_model()

# Create your views here.
def register(request):

    # Handle form submission
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            print('Email already in use.')
            # Render the form again with an inline field error and preserve entered values
            return render(request, 'users/RegPage.html', {
                'error_email': 'Email already in use.',
                'username': username,
                'email': email,
            })
            
        # If email is unique, proceed to create user
        else:
            # Create new user with form data
            print('Creating user:', username, email)
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save() # Save the user to the database
            return redirect('/')
    else:
        return render(request, 'users/RegPage.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # authenticate() checks the hash and the email
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            auth.login(request, user)  # Assigns this session with the user logged in 
            return redirect('/')
        else:
            return render(request, 'users/LoginPage.html', {
                'error': 'Invalid Details.',
                'email': email,
            })
    else:    
        return render(request, 'users/LoginPage.html')
    
def logout(request):
    auth.logout(request)    # Simple just logouts the user
    print('User logged out.')
    return redirect('/')    
