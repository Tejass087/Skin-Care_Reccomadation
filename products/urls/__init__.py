from django.urls import path
from products import views

app_name = 'products'  # Define the app namespace

urlpatterns = [
    path('', views.home, name='home'),  # This defines the home URL pattern
]