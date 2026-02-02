from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # This is linked to a button in the base.html template that has a tag "action = {% url 'users:register or login' %}"
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
]