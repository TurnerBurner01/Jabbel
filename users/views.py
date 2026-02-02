from django.shortcuts import render

# Create your views here.
def register_view(request):
    return render(request, 'users/RegPage.html')

def login_view(request):
    return render(request, 'users/LoginPage.html')
