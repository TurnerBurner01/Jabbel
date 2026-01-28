from django.urls import path
from . import views

urlpatterns = [
    # This calls the home function in views.py in journals app when the root URL is accessed (' ')
    path('', views.home, name='home'), 
]