# /products/urls/makeup.py

from django.urls import path
from products import views

app_name = 'makeup'  # Required for namespace

urlpatterns = [
    path('', views.makeup, name='index'),
    path('<int:product_id>/', views.makeup_detail, name='detail'),
]