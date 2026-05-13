import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UserPreferenceModel:
    """A model to predict user preferences based on their profile and behavior."""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoders = {}
        self.scaler = MinMaxScaler()
        self.feature_columns = []
        self.target_column = 'preferred_category'
    
    def load_data(self, filepath):
        """Load and preprocess the data."""
        logger.info(f"Loading data from {filepath}")
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert to DataFrame and preprocess
        processed_data = []
        for user in data:
            # Extract features from user preferences
            if 'preferences' in user and 'grocery_apps' in user['preferences']:
                user_data = {
                    'user_id': user['user_id'],
                    'age': user['age'],
                    'gender': user['gender'],
                    'location': user['location'],
                    'price_sensitivity': user['preferences']['grocery_apps'].get('price_sensitivity', 'medium'),
                    'discount_preference': int(user['preferences']['grocery_apps'].get('discount_preference', False)),
                    'delivery_speed': user['preferences']['grocery_apps'].get('delivery_speed_importance', 'standard'),
                    'order_size': user['preferences']['grocery_apps'].get('usual_order_size', '2-3 people'),
                    'preferred_category': user['preferences']['grocery_apps']['preferred_categories'][0]  # Use first category as target
                }
                processed_data.append(user_data)
        
        return pd.DataFrame(processed_data)
    
    def preprocess_data(self, df):
        """Preprocess the data for training."""
        logger.info("Preprocessing data...")
        
        # Encode categorical variables
        categorical_cols = ['gender', 'location', 'price_sensitivity', 'delivery_speed', 'order_size']
        
        # Fit and transform training data, or just transform test data
        if not self.label_encoders:
            # This is training data, fit the encoders
            for col in categorical_cols:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                self.label_encoders[col] = le
        else:
            # This is test data, transform using existing encoders
            for col in categorical_cols:
                le = self.label_encoders[col]
                # Handle unseen labels by assigning a new value
                mask = ~df[col].isin(le.classes_)
                if mask.any():
                    logger.warning(f"Found new categories in {col} that were not seen during training"
                                 f" {df.loc[mask, col].unique()}")
                    # Replace unseen categories with the most frequent category
                    df.loc[mask, col] = le.classes_[0]
                df[col] = le.transform(df[col])
        
        # Define feature and target columns
        self.feature_columns = ['age', 'gender', 'location', 'price_sensitivity', 
                              'discount_preference', 'delivery_speed', 'order_size']
        
        X = df[self.feature_columns]
        y = df[self.target_column]
        
        # Encode target variable
        if 'target_encoder' not in self.label_encoders:
            le = LabelEncoder()
            y = le.fit_transform(y)
            self.label_encoders['target_encoder'] = le
        else:
            le = self.label_encoders['target_encoder']
            y = le.transform(y)
        
        return X, y
    
    def train(self, train_file):
        """Train the model on the training data."""
        logger.info("Starting model training...")
        
        # Load and preprocess training data
        train_df = self.load_data(train_file)
        X_train, y_train = self.preprocess_data(train_df)
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        # Log feature importances
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Feature importances:\n" + str(feature_importance))
        logger.info("Model training completed.")
    
    def evaluate(self, test_file):
        """Evaluate the model on the test data."""
        logger.info("Evaluating model on test data...")
        
        # Load and preprocess test data
        test_df = self.load_data(test_file)
        X_test, y_test = self.preprocess_data(test_df)
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Get the classes present in the test set
        unique_classes = set(y_test)
        target_names = [self.label_encoders['target_encoder'].classes_[i] 
                       for i in range(len(self.label_encoders['target_encoder'].classes_)) 
                       if i in unique_classes]
        
        # Print classification report
        report = classification_report(
            y_test, 
            y_pred,
            labels=list(unique_classes),
            target_names=target_names,
            zero_division=0
        )
        logger.info("\n" + report)
        
        return report
    
    def save_model(self, model_dir='models'):
        """Save the model and encoders to disk."""
        model_dir = Path(model_dir)
        model_dir.mkdir(exist_ok=True)
        
        # Save the model
        model_path = model_dir / 'user_preference_model.joblib'
        joblib.dump(self.model, model_path)
        
        # Save the encoders
        encoders_path = model_dir / 'encoders.joblib'
        joblib.dump(self.label_encoders, encoders_path)
        
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Encoders saved to {encoders_path}")
        
        return {
            'model_path': str(model_path),
            'encoders_path': str(encoders_path)
        }

def main():
    # Initialize the model
    model = UserPreferenceModel()
    
    # File paths
    train_file = 'data/train_users.json'
    test_file = 'data/test_users.json'
    
    # Train the model
    model.train(train_file)
    
    # Evaluate the model
    model.evaluate(test_file)
    
    # Save the model
    model.save_model()
    
    logger.info("Training and evaluation completed successfully!")

if __name__ == "__main__":
    main()
