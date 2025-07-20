# /products/urls/cosmetics.py
from django.urls import path
from products import views

app_name = 'cosmetics'  # Required for namespace
urlpatterns = [
    path('', views.cosmetics, name='index'),
    path('<int:product_id>/', views.cosmetic_detail, name='detail'),
]