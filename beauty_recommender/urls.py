from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls', namespace='products')),  # Add namespace here
    path('skincare/', include('products.urls.skincare', namespace='skincare')),
    path('makeup/', include('products.urls.makeup', namespace='makeup')),
]