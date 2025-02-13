#/products/management/commands/import_data.py

from django.core.management.base import BaseCommand
from products.models import SkincareProduct, MakeupProduct
import csv
import os
from django.conf import settings
from decimal import Decimal
import re

class Command(BaseCommand):
    help = 'Import product data from CSV files'

    def clean_price(self, price_str):
        """Convert price string to float, handling different currency formats."""
        if not price_str or price_str.isspace():
            return Decimal('0.00')
            
        # Remove currency symbols, spaces, and normalize
        price_str = price_str.strip()
        price_str = re.sub(r'[^\d.,]', '', price_str)  # Remove all non-numeric chars except . and ,
        
        # Handle Indonesian Rupiah format (no decimal places)
        if price_str.isdigit():
            return Decimal(price_str) / 100  # Convert to standard decimal format
            
        # Handle USD format ($xx.xx)
        if '.' in price_str:
            # Ensure we only have one decimal point
            parts = price_str.split('.')
            if len(parts) > 2:
                price_str = parts[0] + '.' + parts[1]
            return Decimal(price_str)
            
        return Decimal('0.00')

    def clean_skin_types(self, skin_types_str):
        """Convert various skin type formats to standardized list."""
        if not skin_types_str:
            return ''
            
        # Handle string list format
        if isinstance(skin_types_str, str):
            # Remove brackets and quotes
            cleaned = skin_types_str.strip('[]\'\" ')
            # Split on commas and clean each type
            types = [t.strip(' \'\"') for t in cleaned.split(',') if t.strip()]
            return ','.join(types)
            
        return ''

    def find_file(self, possible_locations):
        """Find file from list of possible locations."""
        for loc in possible_locations:
            if os.path.exists(loc):
                self.stdout.write(f"Found file at: {loc}")
                return loc
        return None

    def import_skincare_products(self, file_path):
        """Import skincare products from CSV."""
        success_count = 0
        error_count = 0
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Map CSV fields to model fields
                    product = SkincareProduct(
                        Skin_type=row.get('skin_type', '').strip(),
                        Product=row.get('Product', '').strip(),
                        Concern=row.get('Concern', '').strip(),
                        product_url=row.get('product_url', '').strip(),
                        product_pic=row.get('product_pic', '').strip(),
                    )
                    product.save()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Error importing skincare product: {str(e)}\nRow: {row}')
                    )
                    
        return success_count, error_count

    def import_makeup_products(self, file_path):
        """Import makeup products from CSV."""
        success_count = 0
        error_count = 0
        
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                        
                    product = MakeupProduct(
                        name=row.get('name', '').strip(),
                        brand=row.get('brand', '').strip(),
                        price=self.clean_price(row.get('price', '0')),
                        rank=float(row.get('rank', 0)) if row.get('rank') else 0.0,
                        skin_type=self.clean_skin_types(row.get('skin_type')),
                        ingredients=row.get('ingredients', '').strip()
                    )
                    product.save()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'Error importing makeup product: {str(e)}\nRow: {row}')
                    )
                    
        return success_count, error_count

    def handle(self, *args, **kwargs):
        # Define possible file locations
        possible_locations_skincare = [
            'data/skincare.csv',
            'skincare.csv',
            os.path.join(settings.BASE_DIR, 'data', 'skincare.csv'),
            os.path.join(settings.BASE_DIR, 'skincare.csv'),
        ]

        possible_locations_makeup = [
            'data/cosmetic.csv',
            'cosmetic.csv',
            os.path.join(settings.BASE_DIR, 'data', 'cosmetic.csv'),
            os.path.join(settings.BASE_DIR, 'cosmetic.csv'),
        ]

        # Import skincare products
        skincare_file = self.find_file(possible_locations_skincare)
        if skincare_file:
            success, errors = self.import_skincare_products(skincare_file)
            self.stdout.write(self.style.SUCCESS(
                f'Skincare import completed: {success} successful, {errors} errors'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"Could not find skincare CSV file. Tried: {', '.join(possible_locations_skincare)}"
            ))

        # Import makeup products
        makeup_file = self.find_file(possible_locations_makeup)
        if makeup_file:
            success, errors = self.import_makeup_products(makeup_file)
            self.stdout.write(self.style.SUCCESS(
                f'Makeup import completed: {success} successful, {errors} errors'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"Could not find makeup CSV file. Tried: {', '.join(possible_locations_makeup)}"
            ))
