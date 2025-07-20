# /products/views.py

from django.shortcuts import render, get_object_or_404
from .models import SkincareProduct, CosmeticProduct
from .forms import SkincareFilterForm, CosmeticFilterForm
from .recommendation import ProductRecommender
import pandas as pd
from django import forms

# Initialize recommender instance
recommender = ProductRecommender()

def home(request):
    return render(request, "home.html")

def initialize_recommender():
    """Fetch data from the database and prepare it for the recommender system."""
    skincare_products = list(SkincareProduct.objects.values())
    cosmetic_products = list(CosmeticProduct.objects.values())

    # Convert to DataFrame and prepare data
    recommender.prepare_skincare_data(pd.DataFrame(skincare_products))
    recommender.prepare_cosmetic_data(pd.DataFrame(cosmetic_products))



def skincare(request):
    """Handles skincare product recommendations based on user filters."""
    form = SkincareFilterForm(request.GET)
    products = SkincareProduct.objects.all()

    if form.is_valid():
        skin_type = form.cleaned_data.get('skin_type')
        concern = form.cleaned_data.get('concern')

        if skin_type:
            products = products.filter(Skin_type__icontains=skin_type)
        if concern:
            products = products.filter(Concern__icontains=concern)

    return render(request, 'skincare/index.html', {'form': form, 'products': products})

def skincare_detail(request, product_id):
    """Displays details for a specific skincare product."""
    product = get_object_or_404(SkincareProduct, id=product_id)
    return render(request, 'skincare/product_detail.html', {'product': product})

def cosmetics(request):
    """Handles cosmetic product recommendations based on user filters."""
    form = CosmeticFilterForm(request.GET)
    products = CosmeticProduct.objects.all()
    
    if form.is_valid():
        category = form.cleaned_data.get('category')
        subcategory = form.cleaned_data.get('subcategory')
        brand = form.cleaned_data.get('brand')
        min_rating = form.cleaned_data.get('min_rating')
        max_price = form.cleaned_data.get('max_price')
        
        # Apply filters directly
        if category:
            products = products.filter(category=category)
        if subcategory:
            products = products.filter(subcategory=subcategory)
        if brand:
            products = products.filter(brand__icontains=brand)
        if min_rating is not None:
            products = products.filter(rating__gte=min_rating)
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        
        # If you want to use the recommender system instead:
        # try:
        #     recommended_products = recommender.get_cosmetic_recommendations(
        #         category=category, subcategory=subcategory, brand=brand, 
        #         min_rating=min_rating, max_price=max_price
        #     )
        #     products = CosmeticProduct.objects.filter(
        #         id__in=[p['id'] for p in recommended_products.to_dict('records')]
        #     )
        # except Exception as e:
        #     print(f"Error in cosmetic recommendations: {e}")
    
    return render(request, 'cosmetics/index.html', {'form': form, 'products': products})

def cosmetic_detail(request, product_id):
    """Displays details for a specific cosmetic product."""
    product = get_object_or_404(CosmeticProduct, id=product_id)
    return render(request, 'cosmetics/product_detail.html', {'product': product})


