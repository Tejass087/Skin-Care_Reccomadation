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

class MakeupProduct(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rank = models.FloatField()  # Keep using rank instead of rating to match existing data
    skin_type = models.CharField(max_length=200)
    ingredients = models.TextField()
    
    class Meta:
        indexes = [
            models.Index(fields=['skin_type']),
            models.Index(fields=['rank']),  # Keep using rank in index
        ]
