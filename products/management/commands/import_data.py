from django.core.management.base import BaseCommand
from products.models import SkincareProduct, CosmeticProduct
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
        """Import makeup products from CSV with robust error handling."""
        success_count = 0
        error_count = 0
        
        # Try different encodings
        encodings = ['latin-1', 'ISO-8859-1', 'cp1252', 'utf-8', 'utf-8-sig']
        
        for encoding in encodings:
            try:
                self.stdout.write(f"Trying encoding: {encoding}")
                with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                    # Read the entire file first
                    content = file.read()
                    
                    # Create a file-like object from the content
                    import io
                    csv_file = io.StringIO(content)
                    
                    reader = csv.DictReader(csv_file)
                    rows_processed = 0
                    
                    for row in reader:
                        try:
                            rows_processed += 1
                            # Skip empty rows
                            if not any(row.values()):
                                continue
                                
                            # Handle empty or invalid rating field
                            rating = row.get('rating', '0')
                            if rating == '' or rating is None:
                                rating = 0
                            else:
                                try:
                                    rating = float(rating)
                                except ValueError:
                                    rating = 0
                            
                            # Handle price field
                            price = row.get('price', '0')
                            if price == '' or price is None:
                                price = '0'
                            
                            product = CosmeticProduct(
                                product_name=row.get('product_name', ''),
                                website=row.get('website', ''),
                                country=row.get('country', ''),
                                category=row.get('category', ''),
                                subcategory=row.get('subcategory', ''),
                                title_href=row.get('title-href', ''),
                                price=price,
                                brand=row.get('brand', ''),
                                ingredients=row.get('ingredients', ''),
                                form=row.get('form', ''),
                                type=row.get('type', ''),
                                color=row.get('color', ''),
                                size=row.get('size', '0'),
                                rating=rating,
                                noofratings=row.get('noofratings', '0')
                            )
                            product.save()
                            success_count += 1
                            
                            # Print progress every 100 rows
                            if success_count % 100 == 0:
                                self.stdout.write(f"Successfully imported {success_count} products")
                                
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.WARNING(f'Error importing makeup product: {str(e)}\nRow: {row}')
                            )
                            
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully read file with encoding: {encoding}. Processed {rows_processed} rows.'
                    ))
                    return success_count, error_count
                            
            except UnicodeDecodeError as e:
                self.stdout.write(self.style.WARNING(f'Failed to read file with encoding: {encoding}. Error: {str(e)}'))
                # Continue to the next encoding
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Unexpected error with encoding {encoding}: {str(e)}'))
                # Try the next encoding
                continue
        
        self.stdout.write(self.style.ERROR('Could not read the file with any of the attempted encodings.'))            
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
            'data/cosmeticdataset.csv',
            'cosmeticdataset.csv',
            os.path.join(settings.BASE_DIR, 'data', 'cosmeticdataset.csv'),
            os.path.join(settings.BASE_DIR, 'cosmeticdataset.csv'),
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