from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls', namespace='products')),  # Add namespace here
    path('skincare/', include('products.urls.skincare', namespace='skincare')),
    path('cosmetics/', include('products.urls.cosmetics', namespace='cosmetics')),
    path('virtual-makeup/', include('products.urls.virtual_makeup', namespace='virtual_makeup')),
]