import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import LabelEncoder
import joblib
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set style for plots
plt.style.use('ggplot')
sns.set_palette("husl")

# Create plots directory if it doesn't exist
os.makedirs('plots', exist_ok=True)

class ModelVisualizer:
    def __init__(self, data_path, model_path='models/user_preference_model.joblib', 
                 encoders_path='models/encoders.joblib'):
        self.data_path = data_path
        self.model_path = model_path
        self.encoders_path = encoders_path
        self.data = None
        self.model = None
        self.label_encoders = None
        self.X = None
        self.y = None
        self.y_pred = None
        self.classes = None
        
    def load_data(self):
        """Load and preprocess the data."""
        logger.info(f"Loading data from {self.data_path}")
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
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
        
        self.data = pd.DataFrame(processed_data)
        
        # Load model and encoders
        self.model = joblib.load(self.model_path)
        self.label_encoders = joblib.load(self.encoders_path)
        
        # Preprocess data
        X = self.data.copy()
        
        # Encode categorical variables
        categorical_cols = ['gender', 'location', 'price_sensitivity', 'delivery_speed', 'order_size']
        for col in categorical_cols:
            le = self.label_encoders[col]
            X[col] = le.transform(X[col])
        
        # Define features and target
        self.feature_columns = ['age', 'gender', 'location', 'price_sensitivity', 
                              'discount_preference', 'delivery_speed', 'order_size']
        
        self.X = X[self.feature_columns]
        self.y = self.label_encoders['target_encoder'].transform(self.data['preferred_category'])
        self.classes = self.label_encoders['target_encoder'].classes_
        
        # Make predictions
        self.y_pred = self.model.predict(self.X)
        
    def plot_class_distribution(self):
        """Plot the distribution of classes in the dataset."""
        plt.figure(figsize=(12, 6))
        ax = sns.countplot(y='preferred_category', data=self.data, 
                          order=self.data['preferred_category'].value_counts().index)
        plt.title('Distribution of Preferred Categories')
        plt.xlabel('Count')
        plt.ylabel('Category')
        plt.tight_layout()
        plt.savefig('plots/class_distribution.png')
        plt.close()
        
    def plot_feature_importance(self):
        """Plot feature importance from the trained model."""
        importance = self.model.feature_importances_
        indices = np.argsort(importance)[::-1]
        
        plt.figure(figsize=(10, 6))
        plt.title('Feature Importance')
        plt.bar(range(len(importance)), importance[indices])
        plt.xticks(range(len(importance)), 
                  [self.feature_columns[i] for i in indices], 
                  rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('plots/feature_importance.png')
        plt.close()
        
    def plot_confusion_matrix(self):
        """Plot a normalized confusion matrix."""
        cm = confusion_matrix(self.y, self.y_pred)
        cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(cm_normalized, annot=True, fmt='.2f', 
                   xticklabels=self.classes, 
                   yticklabels=self.classes,
                   cmap='Blues')
        plt.title('Normalized Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('plots/confusion_matrix.png')
        plt.close()
        
    def plot_age_vs_category(self):
        """Plot the relationship between age and preferred categories."""
        plt.figure(figsize=(14, 8))
        sns.boxplot(x='preferred_category', y='age', data=self.data)
        plt.title('Age Distribution by Preferred Category')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('plots/age_vs_category.png')
        plt.close()
        
    def plot_category_by_location(self):
        """Plot the distribution of categories across different locations."""
        cross_tab = pd.crosstab(self.data['location'], 
                               self.data['preferred_category'], 
                               normalize='index')
        
        plt.figure(figsize=(14, 8))
        sns.heatmap(cross_tab, annot=True, cmap='YlGnBu', fmt='.2f')
        plt.title('Category Distribution by Location')
        plt.xlabel('Preferred Category')
        plt.ylabel('Location')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('plots/category_by_location.png')
        plt.close()
        
    def plot_delivery_speed_preference(self):
        """Plot the relationship between delivery speed preference and categories."""
        plt.figure(figsize=(14, 8))
        sns.countplot(y='delivery_speed', hue='preferred_category', 
                     data=self.data, palette='viridis')
        plt.title('Delivery Speed Preference by Category')
        plt.xlabel('Count')
        plt.ylabel('Delivery Speed Importance')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('plots/delivery_speed_preference.png')
        plt.close()
        
    def plot_discount_preference_impact(self):
        """Plot the impact of discount preference on category selection."""
        plt.figure(figsize=(14, 8))
        sns.countplot(y='preferred_category', hue='discount_preference', 
                     data=self.data, palette='muted')
        plt.title('Discount Preference Impact on Category Selection')
        plt.xlabel('Count')
        plt.ylabel('Preferred Category')
        plt.legend(title='Prefers Discounts', labels=['No', 'Yes'])
        plt.tight_layout()
        plt.savefig('plots/discount_preference_impact.png')
        plt.close()
        
    def plot_order_size_distribution(self):
        """Plot the distribution of order sizes by category."""
        plt.figure(figsize=(14, 8))
        sns.countplot(y='order_size', hue='preferred_category', 
                     data=self.data, palette='Set2')
        plt.title('Order Size Distribution by Category')
        plt.xlabel('Count')
        plt.ylabel('Order Size')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig('plots/order_size_distribution.png')
        plt.close()
        
    def generate_all_plots(self):
        """Generate all plots and save them to the plots directory."""
        # Ensure the plots directory exists
        os.makedirs('plots', exist_ok=True)
        
        # Generate all plots
        logger.info("Generating visualizations...")
        
        self.plot_class_distribution()
        logger.info("✓ Class distribution plot generated")
        
        self.plot_feature_importance()
        logger.info("✓ Feature importance plot generated")
        
        self.plot_confusion_matrix()
        logger.info("✓ Confusion matrix generated")
        
        self.plot_age_vs_category()
        logger.info("✓ Age vs. category plot generated")
        
        self.plot_category_by_location()
        logger.info("✓ Category by location plot generated")
        
        self.plot_delivery_speed_preference()
        logger.info("✓ Delivery speed preference plot generated")
        
        self.plot_discount_preference_impact()
        logger.info("✓ Discount preference impact plot generated")
        
        self.plot_order_size_distribution()
        logger.info("✓ Order size distribution plot generated")
        
        logger.info(f"All visualizations saved to the 'plots' directory")

if __name__ == "__main__":
    # Initialize the visualizer
    visualizer = ModelVisualizer(data_path='synthetic_users_250.json')
    
    try:
        # Load data and generate plots
        visualizer.load_data()
        visualizer.generate_all_plots()
        
        logger.info("Visualization process completed successfully!")
        
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        raise
