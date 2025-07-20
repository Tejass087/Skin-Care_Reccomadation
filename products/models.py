# /products/models.py

from django.db import models

class SkincareProduct(models.Model):
    Skin_type = models.CharField(max_length=100)  # Ensure this field exists
    Product = models.CharField(max_length=200)
    Concern = models.CharField(max_length=200)
    product_url = models.URLField()
    product_pic = models.URLField()

    def __str__(self):
        return self.Product

    class Meta:
        indexes = [
            models.Index(fields=['Skin_type']),
            models.Index(fields=['Concern']),
        ]

# /products/models.py (add this new model)
class CosmeticProduct(models.Model):
    product_name = models.CharField(max_length=255)
    website = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    title_href = models.URLField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=100)
    ingredients = models.TextField(null=True, blank=True)
    form = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    noofratings = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.product_name
    
    class Meta:
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['subcategory']),
            models.Index(fields=['brand']),
            models.Index(fields=['rating']),
        ]
