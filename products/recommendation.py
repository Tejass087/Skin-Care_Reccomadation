# /products/recommendation.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ProductRecommender:
    def __init__(self):
        self.skincare_data = None
        self.makeup_data = None
        self.cosmetic_data = None
        self.skincare_vectorizer = TfidfVectorizer(stop_words='english')
        self.makeup_vectorizer = TfidfVectorizer(stop_words='english')
        self.cosmetic_vectorizer = TfidfVectorizer(stop_words='english')
        
    def prepare_skincare_data(self, df):
        self.skincare_data = df
        # Combine relevant features for similarity calculation
        text_features = df['notable_effects'] + ' ' + df['description']
        self.skincare_tfidf = self.skincare_vectorizer.fit_transform(text_features)
        
    def prepare_makeup_data(self, df):
        self.makeup_data = df
        # Combine relevant features for similarity calculation
        text_features = df['ingredients']
        self.makeup_tfidf = self.makeup_vectorizer.fit_transform(text_features)
    
    def get_skincare_recommendations(self, skin_type, concerns, max_price=None):
        # Filter by skin type
        mask = self.skincare_data['skintype'].str.contains(skin_type, na=False)
        if max_price:
            mask &= self.skincare_data['price'] <= max_price
            
        filtered_data = self.skincare_data[mask]
        
        if filtered_data.empty:
            return []
            
        # Calculate similarity based on concerns
        query_vector = self.skincare_vectorizer.transform([concerns])
        similarities = cosine_similarity(query_vector, 
                                      self.skincare_tfidf[filtered_data.index])
        
        # Get top recommendations
        top_indices = similarities[0].argsort()[-5:][::-1]
        return filtered_data.iloc[top_indices]
    
    def prepare_cosmetic_data(self, df):
        self.cosmetic_data = df
        # Combine relevant features for similarity calculation
        df['ingredients'] = df['ingredients'].fillna('')
        df['type'] = df['type'].fillna('')
        df['form'] = df['form'].fillna('')
        text_features = df['ingredients'] + ' ' + df['type'] + ' ' + df['form']
        self.cosmetic_tfidf = self.cosmetic_vectorizer.fit_transform(text_features)
    
    def get_cosmetic_recommendations(self, category=None, subcategory=None, brand=None, min_rating=None, max_price=None):
        # Start with all data
        mask = pd.Series(True, index=self.cosmetic_data.index)
        
        # Apply filters
        if category and category != '':
            mask &= self.cosmetic_data['category'] == category
        
        # Add subcategory filter
        if subcategory and subcategory != '':
            mask &= self.cosmetic_data['subcategory'] == subcategory
        
        if brand and brand != '':
            mask &= self.cosmetic_data['brand'].str.contains(brand, case=False, na=False)
        
        if min_rating is not None:
            mask &= self.cosmetic_data['rating'] >= min_rating
        
        if max_price is not None:
            mask &= self.cosmetic_data['price'] <= max_price
        
        filtered_data = self.cosmetic_data[mask]
        
        if filtered_data.empty:
            return pd.DataFrame()
        
        # Get top rated products from filtered data
        return filtered_data.sort_values(by='rating', ascending=False).head(10)

