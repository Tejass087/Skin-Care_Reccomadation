# /products/recommendation.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class ProductRecommender:
    def __init__(self):
        self.skincare_data = None
        self.makeup_data = None
        self.skincare_vectorizer = TfidfVectorizer(stop_words='english')
        self.makeup_vectorizer = TfidfVectorizer(stop_words='english')
        
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
    
    def get_makeup_recommendations(self, skin_type, preferences, min_rating=None):
        # Filter by skin type and rating (using rank)
        mask = self.makeup_data['skin_type'].str.contains(skin_type, na=False, case=False)
        if min_rating:
            mask &= self.makeup_data['rank'] >= min_rating  # Use rank instead of rating
            
        filtered_data = self.makeup_data[mask]
        if filtered_data.empty:
            return []
            
        # Combine ingredients and description for better matching
        text_features = filtered_data['ingredients'] + ' ' + filtered_data['description'].fillna('')
        makeup_tfidf = self.makeup_vectorizer.fit_transform(text_features)
        
        # Calculate similarity based on preferences
        query_vector = self.makeup_vectorizer.transform([preferences])
        similarities = cosine_similarity(query_vector, makeup_tfidf)
        
        # Get top recommendations
        top_indices = similarities[0].argsort()[-5:][::-1]
        return filtered_data.iloc[top_indices]

