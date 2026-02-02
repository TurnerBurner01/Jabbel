from django.shortcuts import render

# Create your views here.
def register(request):
    return render(request, 'users/RegPage.html')

def login(request):
    return render(request, 'users/LoginPage.html')
