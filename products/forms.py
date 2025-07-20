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

class CosmeticFilterForm(forms.Form):
    CATEGORY_CHOICES = [
        ('', 'All Categories'),
        ('eyes', 'Eyes'),
        ('face', 'Face'),
        ('lips', 'Lips'),
        ('body', 'Body'),
        ('skincare', 'Skincare'),
        ('hair', 'Hair'),
    ]

    SUBCATEGORY_CHOICES = {
        'eyes': [
            ('', 'All Eye Products'),
            ('eyeliner', 'Eyeliner'),
            ('mascara', 'Mascara'),
            ('eyeshadow', 'Eyeshadow'),
            ('eyebrow', 'Eyebrow'),
            ('eyelashes', 'Eyelashes'),
            ('primer', 'Eye Primer')
        ],
        'face': [
            ('', 'All Face Products'),
            ('foundation', 'Foundation'),
            ('concealer', 'Concealer'),
            ('blush', 'Blush'),
            ('highlighter', 'Highlighter'),
            ('primer', 'Primer'),
            ('powder', 'Powder')
        ],
        'lips': [
            ('', 'All Lip Products'),
            ('lipstick', 'Lipstick'),
            ('lipgloss', 'Lip Gloss'),
            ('lipliner', 'Lip Liner'),
            ('lipbalm', 'Lip Balm'),
            ('lipstain', 'Lip Stain')
        ],
        'body': [
            ('', 'All Body Products'),
            ('perfume', 'Perfume'),
            ('soap', 'Soap'),
            ('bodywash', 'Body Wash'),
            ('sunscreen', 'Sunscreen'),
            ('moisturizer', 'Moisturizer')
        ],
        'skincare': [
            ('', 'All Skincare Products'),
            ('moisturizer', 'Moisturizer'),
            ('cleanser', 'Cleanser'),
            ('eye treatment', 'Eye Treatment'),
            ('serum', 'Serum'),
            ('toner', 'Toner'),
            ('spray', 'Spray')
        ],
        'hair': [
            ('', 'All Hair Products'),
            ('shampoo', 'Shampoo'),
            ('conditioner', 'Conditioner'),
            ('oil', 'Hair Oil'),
            ('hairstyling', 'Hair Styling'),
            ('shampoo', 'Dry Shampoo'),
            ('serum', 'Hair Serum')
        ]
    }
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500',
            'id': 'id_category'
        })
    )
    
    subcategory = forms.ChoiceField(
        choices=[],  # Empty initially, will be populated via JavaScript
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500',
            'id': 'id_subcategory'
        })
    )
    
    brand = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500',
            'placeholder': 'Enter brand name'
        })
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
    
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-pink-500 focus:ring-pink-500',
            'placeholder': 'Maximum price',
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize subcategory choices based on the selected category
        if 'category' in self.data:
            try:
                category = self.data.get('category')
                self.fields['subcategory'].choices = self.SUBCATEGORY_CHOICES.get(category, [('', 'All Subcategories')])
            except (ValueError, TypeError):
                pass  # Invalid input from the client; ignore and fallback to empty choices
        else:
            self.fields['subcategory'].choices = [('', 'All Subcategories')]