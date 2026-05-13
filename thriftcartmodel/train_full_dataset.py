import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score
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
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            bootstrap=True,
            class_weight='balanced',
            random_state=42
        )
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
                    'preferred_category': user['preferences']['grocery_apps']['preferred_categories'][0]
                }
                processed_data.append(user_data)
        
        return pd.DataFrame(processed_data)
    
    def preprocess_data(self, df, is_training=True):
        """Preprocess the data for training or inference."""
        logger.info("Preprocessing data...")
        
        # Make a copy to avoid modifying the original DataFrame
        df = df.copy()
        
        # Encode categorical variables
        categorical_cols = ['gender', 'location', 'price_sensitivity', 'delivery_speed', 'order_size']
        
        if is_training:
            # Fit and transform training data
            for col in categorical_cols:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col])
                self.label_encoders[col] = le
            
            # Encode target variable
            le = LabelEncoder()
            y = le.fit_transform(df[self.target_column])
            self.label_encoders['target_encoder'] = le
        else:
            # Transform test/validation data
            for col in categorical_cols:
                le = self.label_encoders[col]
                # Handle unseen labels by assigning the most frequent category
                mask = ~df[col].isin(le.classes_)
                if mask.any():
                    logger.warning(f"Found new categories in {col} that were not seen during training")
                    # Replace unseen categories with the most frequent category
                    df.loc[mask, col] = le.classes_[0]
                df[col] = le.transform(df[col])
            
            le = self.label_encoders['target_encoder']
            y = le.transform(df[self.target_column])
        
        # Define feature columns
        self.feature_columns = ['age', 'gender', 'location', 'price_sensitivity', 
                              'discount_preference', 'delivery_speed', 'order_size']
        
        X = df[self.feature_columns]
        
        return X, y
    
    def train(self, train_file, test_size=0.2):
        """Train the model on the training data."""
        logger.info("Starting model training...")
        
        # Load and preprocess training data
        df = self.load_data(train_file)
        
        # Split the data into training and validation sets
        train_df, val_df = train_test_split(
            df, 
            test_size=test_size, 
            random_state=42,
            stratify=df[self.target_column]
        )
        
        logger.info(f"Training set size: {len(train_df)}, Validation set size: {len(val_df)}")
        
        # Preprocess the training data
        X_train, y_train = self.preprocess_data(train_df, is_training=True)
        
        # Train the model with cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            self.model, X_train, y_train, 
            cv=cv, scoring='accuracy', n_jobs=-1
        )
        
        logger.info(f"Cross-validation accuracy: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
        
        # Train the final model on the full training set
        self.model.fit(X_train, y_train)
        
        # Log feature importances
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Feature importances:\n" + str(feature_importance))
        
        # Evaluate on validation set
        if len(val_df) > 0:
            X_val, y_val = self.preprocess_data(val_df, is_training=False)
            y_pred = self.model.predict(X_val)
            
            # Get the classes present in the validation set
            unique_classes = np.unique(y_val)
            target_names = [self.label_encoders['target_encoder'].classes_[i] 
                          for i in range(len(self.label_encoders['target_encoder'].classes_)) 
                          if i in unique_classes]
            
            # Print classification report
            report = classification_report(
                y_val, 
                y_pred,
                labels=unique_classes,
                target_names=target_names,
                zero_division=0
            )
            logger.info("\nValidation Report:\n" + report)
            
            val_accuracy = accuracy_score(y_val, y_pred)
            logger.info(f"Validation accuracy: {val_accuracy:.4f}")
        
        logger.info("Model training completed.")
        
        return self.model
    
    def evaluate(self, test_file):
        """Evaluate the model on the test data."""
        if self.model is None:
            raise ValueError("Model has not been trained yet. Call train() first.")
        
        logger.info("Evaluating model on test data...")
        
        # Load and preprocess test data
        test_df = self.load_data(test_file)
        X_test, y_test = self.preprocess_data(test_df, is_training=False)
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Get the classes present in the test set
        unique_classes = np.unique(y_test)
        target_names = [self.label_encoders['target_encoder'].classes_[i] 
                       for i in range(len(self.label_encoders['target_encoder'].classes_)) 
                       if i in unique_classes]
        
        # Print classification report
        report = classification_report(
            y_test, 
            y_pred,
            labels=unique_classes,
            target_names=target_names,
            zero_division=0
        )
        logger.info("\nTest Report:\n" + report)
        
        # Calculate and log test accuracy
        test_accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Test accuracy: {test_accuracy:.4f}")
        
        return {
            'report': report,
            'accuracy': test_accuracy,
            'y_true': y_test,
            'y_pred': y_pred
        }
    
    def save_model(self, model_dir='models'):
        """Save the model and encoders to disk."""
        if self.model is None:
            raise ValueError("Model has not been trained yet. Call train() first.")
        
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
    
    # File path
    data_file = 'synthetic_users_250.json'
    
    try:
        # Train the model with a validation split
        model.train(data_file, test_size=0.2)
        
        # Evaluate on the same data (since we don't have a separate test set)
        evaluation = model.evaluate(data_file)
        
        # Save the trained model
        saved_paths = model.save_model()
        
        logger.info("\nModel training and evaluation completed successfully!")
        logger.info(f"Test accuracy: {evaluation['accuracy']:.4f}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
