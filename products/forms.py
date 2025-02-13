# /products/forms.py

from django import forms

class SkincareFilterForm(forms.Form):
    SKIN_TYPES = [
        ('', 'Select Skin Type'),
        ('Normal', 'Normal'),
        ('Oily', 'Oily'),
        ('Dry', 'Dry'),
        ('Combination', 'Combination'),
        ('Sensitive', 'Sensitive'),
    ]

    CONCERN_CHOICES = [
        ('', 'Select Concern'),
        ('Acne', 'Acne'),
        ('Hydration', 'Hydration'),
        ('Sun protection', 'Sun Protection'),
        ('Whitehead/Blackhead', 'Whitehead/Blackhead'),
        ('Pimples', 'Pimples'),
        ('Pigmentation', 'Pigmentation'),
        ('Irritation', 'Irritation'),
    ]

    skin_type = forms.ChoiceField(
        choices=SKIN_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500'})
    )
    
    concern = forms.ChoiceField(
        choices=CONCERN_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500'})
    )

class MakeupFilterForm(forms.Form):
    SKIN_TYPES = [
        ('', 'Select Skin Type'),
        ('Normal', 'Normal'),
        ('Oily', 'Oily'),
        ('Dry', 'Dry'),
        ('Combination', 'Combination'),
        ('Sensitive', 'Sensitive'),
    ]
    
    skin_type = forms.ChoiceField(choices=SKIN_TYPES, required=False)
    preferences = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Describe your makeup preferences (e.g., long-lasting, natural look)"
    )
    min_rating = forms.FloatField(
        required=False,
        min_value=0,
        max_value=5,
        help_text="Minimum product rating (0-5)"
    )