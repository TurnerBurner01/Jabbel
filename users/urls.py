from django.urls import path
from . import views

urlpatterns = [
    # This is linked to a button in the base.html template that has a tag "action = {% url 'login' %}"
    # When the button is clicked, login_view function in views.py is called which renders login.html
    path('login/', views.login_view, name='login'),
]