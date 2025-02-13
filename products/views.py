# /products/views.py

from django.shortcuts import render, get_object_or_404
from .models import SkincareProduct, MakeupProduct
from .forms import SkincareFilterForm, MakeupFilterForm
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
    makeup_products = list(MakeupProduct.objects.values())

    # Convert to DataFrame and prepare data
    recommender.prepare_skincare_data(pd.DataFrame(skincare_products))
    recommender.prepare_makeup_data(pd.DataFrame(makeup_products))

class MakeupFilterForm(forms.Form):
    SKIN_TYPE_CHOICES = [
        ('', 'All Skin Types'),
        ('oily', 'Oily'),
        ('dry', 'Dry'),
        ('combination', 'Combination'),
        ('normal', 'Normal'),
        ('sensitive', 'Sensitive'),
    ]

    PREFERENCES_CHOICES = [
        ('', 'All Preferences'),
        ('matte', 'Matte'),
        ('dewy', 'Dewy'),
        ('natural', 'Natural'),
        ('full-coverage', 'Full Coverage'),
        ('long-lasting', 'Long Lasting'),
    ]

    skin_type = forms.ChoiceField(
        choices=SKIN_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500'})
    )

    preferences = forms.ChoiceField(
        choices=PREFERENCES_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500'})
    )

    min_rating = forms.FloatField(
        required=False,
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500',
            'placeholder': 'Minimum rating',
            'step': '0.1'
        })
    )

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

def makeup(request):
    """Handles makeup product recommendations based on user filters."""
    form = MakeupFilterForm(request.GET)
    products = MakeupProduct.objects.all()

    if form.is_valid():
        skin_type = form.cleaned_data.get('skin_type')
        preferences = form.cleaned_data.get('preferences')
        min_rating = form.cleaned_data.get('min_rating')

        if skin_type or preferences:
            try:
                recommended_products = recommender.get_makeup_recommendations(
                    skin_type=skin_type,
                    preferences=preferences,
                    min_rating=min_rating
                )
                products = MakeupProduct.objects.filter(
                    id__in=[p['id'] for p in recommended_products.to_dict('records')]
                )
            except Exception as e:
                print(f"Error in makeup recommendations: {e}")

    return render(request, 'makeup/index.html', {'form': form, 'products': products})

def makeup_detail(request, product_id):
    """Displays details for a specific makeup product."""
    product = get_object_or_404(MakeupProduct, id=product_id)
    context = {'product': product}
    return render(request, 'makeup/product_detail.html', context)


