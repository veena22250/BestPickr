import json
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import optuna
from optuna.samplers import TPESampler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImprovedUserPreferenceModel:
    """An improved model with cross-validation and hyperparameter tuning to reduce overfitting."""
    
    def __init__(self, n_trials=50):
        self.model = None
        self.label_encoders = {}
        self.scaler = MinMaxScaler()
        self.feature_columns = []
        self.target_column = 'preferred_category'
        self.n_trials = n_trials
        self.best_params = None
    
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
    
    def objective(self, trial, X, y):
        """Objective function for Optuna hyperparameter optimization."""
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 300, step=50),
            'max_depth': trial.suggest_int('max_depth', 3, 20, step=1),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20, step=2),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10, step=1),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None]),
            'bootstrap': trial.suggest_categorical('bootstrap', [True, False]),
            'class_weight': trial.suggest_categorical('class_weight', ['balanced', 'balanced_subsample', None]),
            'random_state': 42
        }
        
        # Perform cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = []
        
        for train_idx, val_idx in cv.split(X, y):
            X_train_fold, X_val_fold = X.iloc[train_idx], X.iloc[val_idx]
            y_train_fold, y_val_fold = y[train_idx], y[val_idx]
            
            model = RandomForestClassifier(**params)
            model.fit(X_train_fold, y_train_fold)
            
            # Use accuracy as the metric to optimize
            y_pred = model.predict(X_val_fold)
            score = accuracy_score(y_val_fold, y_pred)
            cv_scores.append(score)
        
        # Return the mean cross-validation score
        return np.mean(cv_scores)
    
    def tune_hyperparameters(self, X, y):
        """Tune hyperparameters using Optuna."""
        logger.info("Starting hyperparameter tuning...")
        
        study = optuna.create_study(direction='maximize', sampler=TPESampler(seed=42))
        study.optimize(lambda trial: self.objective(trial, X, y), n_trials=self.n_trials)
        
        self.best_params = study.best_params
        logger.info(f"Best hyperparameters: {self.best_params}")
        
        return self.best_params
    
    def train(self, train_file, use_cross_validation=True):
        """Train the model with cross-validation and hyperparameter tuning."""
        logger.info("Starting model training with cross-validation...")
        
        # Load and preprocess training data
        train_df = self.load_data(train_file)
        X_train, y_train = self.preprocess_data(train_df, is_training=True)
        
        if use_cross_validation:
            # Tune hyperparameters
            best_params = self.tune_hyperparameters(X_train, y_train)
            
            # Train final model with best parameters
            self.model = RandomForestClassifier(**best_params, random_state=42)
        else:
            # Use default parameters
            self.model = RandomForestClassifier(random_state=42)
        
        # Perform cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(
            self.model, X_train, y_train, 
            cv=cv, scoring='accuracy', n_jobs=-1
        )
        
        logger.info(f"Cross-validation accuracy: {np.mean(cv_scores):.4f} ± {np.std(cv_scores):.4f}")
        
        # Train final model on full training data
        self.model.fit(X_train, y_train)
        
        # Log feature importances
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("Feature importances:\n" + str(feature_importance))
        
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
        logger.info("\n" + report)
        
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
        model_path = model_dir / 'improved_user_preference_model.joblib'
        joblib.dump(self.model, model_path)
        
        # Save the encoders
        encoders_path = model_dir / 'improved_encoders.joblib'
        joblib.dump(self.label_encoders, encoders_path)
        
        # Save the best parameters
        if self.best_params is not None:
            params_path = model_dir / 'best_params.json'
            with open(params_path, 'w') as f:
                json.dump(self.best_params, f, indent=2)
        
        logger.info(f"Model saved to {model_path}")
        logger.info(f"Encoders saved to {encoders_path}")
        
        return {
            'model_path': str(model_path),
            'encoders_path': str(encoders_path),
            'params_path': str(params_path) if self.best_params is not None else None
        }

def main():
    # Initialize the improved model
    model = ImprovedUserPreferenceModel(n_trials=30)  # Reduced number of trials for faster execution
    
    # File paths
    train_file = 'data/train_users.json'
    test_file = 'data/test_users.json'
    
    try:
        # Train the model with cross-validation and hyperparameter tuning
        model.train(train_file, use_cross_validation=True)
        
        # Evaluate the model on the test set
        evaluation = model.evaluate(test_file)
        
        # Save the trained model
        saved_paths = model.save_model()
        
        logger.info("\nModel training and evaluation completed successfully!")
        logger.info(f"Test accuracy: {evaluation['accuracy']:.4f}")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
