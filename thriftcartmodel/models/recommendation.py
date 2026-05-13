import json
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from config import config
import joblib
import os

class ProductRecommender:
    def __init__(self, n_neighbors=5):
        """
        Initialize the Product Recommender with KNN algorithm.
        
        Args:
            n_neighbors (int): Number of neighbors to consider for recommendations
        """
        self.n_neighbors = n_neighbors
        self.model = None
        self.user_features = None
        self.user_ids = None
        self.feature_processor = None
        self.is_fitted = False
        
    def _preprocess_user_data(self, users_data):
        """Preprocess user data for the recommendation model"""
        # Convert to DataFrame if not already
        if isinstance(users_data, list):
            users_df = pd.json_normalize(users_data)
        else:
            users_df = users_data.copy()
            
        # Store user IDs
        self.user_ids = users_df['user_id'].values
        
        # Define features to use for recommendations
        feature_columns = [
            'age',
            'gender',
            'location',
            'preferences.grocery_apps.preferred_categories',
            'preferences.grocery_apps.price_sensitivity',
            'preferences.ride_services.safety_importance',
            'preferences.ride_services.price_sensitivity',
            'preferences.ecommerce.preferred_categories',
            'preferences.ecommerce.price_sensitivity'
        ]
        
        # Extract features
        features = users_df[feature_columns]
        
        # Define preprocessing for different column types
        categorical_features = [
            'gender', 
            'location',
            'preferences.grocery_apps.preferred_categories',
            'preferences.grocery_apps.price_sensitivity',
            'preferences.ride_services.safety_importance',
            'preferences.ride_services.price_sensitivity',
            'preferences.ecommerce.preferred_categories',
            'preferences.ecommerce.price_sensitivity'
        ]
        
        numeric_features = ['age']
        
        # Create column transformer
        self.feature_processor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numeric_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])
        
        # Preprocess features
        self.user_features = self.feature_processor.fit_transform(features)
        
        return self.user_features
    
    def fit(self, users_data):
        """
        Fit the KNN model on user data
        
        Args:
            users_data (list or DataFrame): List of user dictionaries or DataFrame
        """
        # Preprocess user data
        self._preprocess_user_data(users_data)
        
        # Initialize and fit KNN model
        self.model = NearestNeighbors(
            n_neighbors=self.n_neighbors + 1,  # +1 because user will be their own nearest neighbor
            metric='cosine',
            algorithm='auto'
        )
        self.model.fit(self.user_features)
        self.is_fitted = True
        
        return self
    
    def get_similar_users(self, user_id, n=None):
        """
        Get similar users based on preferences
        
        Args:
            user_id (str): ID of the target user
            n (int, optional): Number of similar users to return. Defaults to None (uses n_neighbors)
            
        Returns:
            list: List of similar user IDs
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
            
        if user_id not in self.user_ids:
            raise ValueError(f"User ID {user_id} not found in the dataset.")
            
        # Get index of the user
        user_idx = np.where(self.user_ids == user_id)[0][0]
        
        # Find nearest neighbors
        distances, indices = self.model.kneighbors(
            self.user_features[user_idx].reshape(1, -1),
            n_neighbors=(n or self.n_neighbors) + 1  # +1 to exclude self
        )
        
        # Exclude the user themselves and get user IDs of similar users
        similar_user_indices = indices[0][1:]  # Skip the first one (user themselves)
        similar_user_ids = [self.user_ids[i] for i in similar_user_indices]
        
        return similar_user_ids
    
    def recommend_products(self, user_id, products_data, n_recommendations=5):
        """
        Recommend products to a user based on similar users' preferences
        
        Args:
            user_id (str): ID of the target user
            products_data (list or DataFrame): List of product dictionaries or DataFrame
            n_recommendations (int, optional): Number of recommendations to return. Defaults to 5.
            
        Returns:
            list: List of recommended product IDs
        """
        # Get similar users
        similar_users = self.get_similar_users(user_id)
        
        # TODO: Implement product recommendation logic based on similar users' preferences
        # This is a placeholder - in a real implementation, you would:
        # 1. Get products that similar users have interacted with/purchased
        # 2. Rank these products based on some scoring metric
        # 3. Return the top N recommendations
        
        # For now, return random products as placeholders
        if isinstance(products_data, pd.DataFrame):
            recommended_products = products_data.sample(min(n_recommendations, len(products_data)))
            return recommended_products['product_id'].tolist()
        else:
            import random
            return random.sample([p['product_id'] for p in products_data], 
                               min(n_recommendations, len(products_data)))
    
    def save(self, filepath):
        """Save the model to disk"""
        if not self.is_fitted:
            raise ValueError("Model not fitted. Nothing to save.")
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model and metadata
        joblib.dump({
            'model': self.model,
            'user_features': self.user_features,
            'user_ids': self.user_ids,
            'feature_processor': self.feature_processor,
            'n_neighbors': self.n_neighbors
        }, filepath)
    
    @classmethod
    def load(cls, filepath):
        """Load a saved model from disk"""
        data = joblib.load(filepath)
        
        # Create new recommender instance
        recommender = cls(n_neighbors=data['n_neighbors'])
        
        # Restore attributes
        recommender.model = data['model']
        recommender.user_features = data['user_features']
        recommender.user_ids = data['user_ids']
        recommender.feature_processor = data['feature_processor']
        recommender.is_fitted = True
        
        return recommender
