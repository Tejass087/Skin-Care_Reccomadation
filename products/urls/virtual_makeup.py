# products/urls/virtual_makeup.py
from django.urls import path
from products.virtual_makeup import views

app_name = 'virtual_makeup'
urlpatterns = [
    # Change the URL pattern to match what you're accessing
    path('skin-analysis/', views.skin_analysis, name='skin_analysis'),
    path('analyze-skin/', views.analyze_skin, name='analyze_skin'),
    path('send-recommendations/', views.send_recommendations_email, name='send_recommendations'),
]