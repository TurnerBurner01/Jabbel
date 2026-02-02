from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # This is linked to a button in the base.html template that has a tag "action = {% url 'register' %}"
    # When the button is clicked, register_view function in views.py is called which renders register.html
    path('register/', views.register_view, name='register'),
]