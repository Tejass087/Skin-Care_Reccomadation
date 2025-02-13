# /products/urls/skincare.py

from django.urls import path
from products import views

app_name = 'skincare'

urlpatterns = [
    path('', views.skincare, name='index'),
    path('<int:product_id>/', views.skincare_detail, name='detail'),  # Using 'detail' as the name
]