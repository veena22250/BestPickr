import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import our custom models
from models.price_predictor import PricePredictor
from models.sentiment import SentimentAnalyzer
from models.recommendation import ProductRecommender
from train_model import UserPreferenceModel
from improve_model import ImprovedUserPreferenceModel

# Set up plotting style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class ModelAccuracyComparison:
    """
    Comprehensive model accuracy comparison for ThriftCart ML models.
    Compares accuracy across price prediction, sentiment analysis, recommendation, and user preference models.
    """
    
    def __init__(self):
        self.results = {}
        self.figures = {}
        
    def generate_synthetic_data(self, n_samples=1000):
        """Generate synthetic data for testing all models."""
        print("🔧 Generating synthetic test data...")
        
        # Price prediction data
        dates = pd.date_range('2023-01-01', periods=n_samples, freq='D')
        prices = 1000 + np.cumsum(np.random.randn(n_samples) * 10) + np.sin(np.arange(n_samples) * 2 * np.pi / 365) * 50
        price_data = pd.DataFrame({
            'date': dates,
            'price': prices
        })
        
        # Sentiment analysis data
        reviews = [
            "This product is amazing! I love it so much.",
            "Terrible quality, would not recommend.",
            "It's okay, nothing special.",
            "Excellent value for money, highly recommended!",
            "Poor customer service and bad product.",
            "Good product but expensive.",
            "Fantastic features and great performance!",
            "Disappointed with the purchase.",
            "Average product, meets expectations.",
            "Outstanding quality and fast delivery!"
        ] * (n_samples // 10)
        
        # User preference data
        user_data = []
        for i in range(n_samples):
            user = {
                'user_id': f'user_{i}',
                'age': np.random.randint(18, 65),
                'gender': np.random.choice(['male', 'female']),
                'location': np.random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata']),
                'preferences': {
                    'grocery_apps': {
                        'price_sensitivity': np.random.choice(['low', 'medium', 'high']),
                        'discount_preference': np.random.choice([True, False]),
                        'delivery_speed_importance': np.random.choice(['fast', 'standard', 'economy']),
                        'usual_order_size': np.random.choice(['1 person', '2-3 people', '4+ people']),
                        'preferred_categories': [np.random.choice(['fruits', 'vegetables', 'dairy', 'snacks', 'beverages'])]
                    }
                }
            }
            user_data.append(user)
        
        return {
            'price_data': price_data,
            'reviews': reviews,
            'user_data': user_data
        }
    
    def test_price_prediction_models(self, price_data):
        """Test different price prediction models."""
        print("\n📈 Testing Price Prediction Models...")
        
        models = {
            'ARIMA': 'arima',
            'SARIMA': 'sarima',
            'Random Forest': 'random_forest',
            'XGBoost': 'xgboost',
            'LightGBM': 'lightgbm',
            'CatBoost': 'catboost'
        }
        
        results = {}
        
        for model_name, model_type in models.items():
            try:
                print(f"  Testing {model_name}...")
                
                # Initialize model
                predictor = PricePredictor(model_type=model_type)
                
                # Split data for testing
                train_size = int(len(price_data) * 0.8)
                train_data = price_data.iloc[:train_size]
                test_data = price_data.iloc[train_size:]
                
                # Fit model
                if model_type in ['arima', 'sarima']:
                    predictor.fit(train_data, date_col='date', value_col='price')
                else:
                    # For tree-based models, we need to create features
                    ts = train_data.set_index('date')['price']
                    predictor.fit(ts)
                
                # Evaluate model
                if model_type in ['arima', 'sarima']:
                    # For time series models, evaluate on test data
                    test_ts = test_data.set_index('date')['price']
                    mae = predictor.evaluate(test_ts, metric='mae')
                    mse = predictor.evaluate(test_ts, metric='mse')
                    rmse = np.sqrt(mse)
                else:
                    # For tree-based models, create test features
                    test_ts = test_data.set_index('date')['price']
                    test_features = predictor._create_features(test_ts)
                    X_test = test_features.drop('value', axis=1)
                    y_test = test_features['value']
                    
                    # Make predictions
                    y_pred = predictor.model.predict(X_test)
                    
                    # Calculate metrics
                    mae = np.mean(np.abs(y_test - y_pred))
                    mse = np.mean((y_test - y_pred) ** 2)
                    rmse = np.sqrt(mse)
                
                # Calculate accuracy-like metric (inverse of normalized error)
                price_range = price_data['price'].max() - price_data['price'].min()
                accuracy = max(0, 1 - (rmse / price_range)) * 100
                
                results[model_name] = {
                    'mae': mae,
                    'mse': mse,
                    'rmse': rmse,
                    'accuracy': accuracy
                }
                
                print(f"    ✓ {model_name}: {accuracy:.2f}% accuracy")
                
            except Exception as e:
                print(f"    ✗ {model_name}: Error - {str(e)}")
                results[model_name] = {
                    'mae': np.nan,
                    'mse': np.nan,
                    'rmse': np.nan,
                    'accuracy': 0
                }
        
        return results
    
    def test_sentiment_analysis_models(self, reviews):
        """Test different sentiment analysis models (TextBlob and VADER only)."""
        print("\n😊 Testing Sentiment Analysis Models...")
        
        models = {
            'TextBlob': 'textblob',
            'VADER': 'vader'
        }
        
        results = {}
        
        # Create ground truth labels (simplified)
        ground_truth = []
        for review in reviews:
            if any(word in review.lower() for word in ['amazing', 'excellent', 'fantastic', 'love', 'great']):
                ground_truth.append('positive')
            elif any(word in review.lower() for word in ['terrible', 'poor', 'bad', 'disappointed']):
                ground_truth.append('negative')
            else:
                ground_truth.append('neutral')
        
        for model_name, method in models.items():
            try:
                print(f"  Testing {model_name}...")
                
                # Initialize analyzer
                analyzer = SentimentAnalyzer(method=method)
                
                correct_predictions = 0
                total_predictions = len(reviews)
                
                for i, review in enumerate(reviews):
                    try:
                        # Analyze sentiment
                        result = analyzer.analyze_sentiment(review)
                        
                        # Extract predicted sentiment
                        predicted = result['sentiment']
                        
                        # Compare with ground truth
                        if predicted == ground_truth[i]:
                            correct_predictions += 1
                            
                    except Exception as e:
                        # If analysis fails, count as incorrect
                        pass
                
                accuracy = (correct_predictions / total_predictions) * 100
                results[model_name] = {
                    'accuracy': accuracy,
                    'correct_predictions': correct_predictions,
                    'total_predictions': total_predictions
                }
                
                print(f"    ✓ {model_name}: {accuracy:.2f}% accuracy")
                
            except Exception as e:
                print(f"    ✗ {model_name}: Error - {str(e)}")
                results[model_name] = {
                    'accuracy': 0,
                    'correct_predictions': 0,
                    'total_predictions': len(reviews)
                }
        
        return results
    
    def test_recommendation_model(self, user_data):
        """Test recommendation model."""
        print("\n🎯 Testing Recommendation Model...")
        
        try:
            # Initialize recommender
            recommender = ProductRecommender(n_neighbors=5)
            
            # Fit the model
            recommender.fit(user_data)
            
            # Test recommendations for a few users
            test_users = user_data[:10]  # Test with first 10 users
            successful_recommendations = 0
            total_recommendations = 0
            
            for user in test_users:
                try:
                    user_id = user['user_id']
                    similar_users = recommender.get_similar_users(user_id, n=3)
                    
                    if len(similar_users) > 0:
                        successful_recommendations += 1
                    total_recommendations += 1
                    
                except Exception as e:
                    pass
            
            accuracy = (successful_recommendations / total_recommendations) * 100 if total_recommendations > 0 else 0
            
            results = {
                'KNN Recommender': {
                    'accuracy': accuracy,
                    'successful_recommendations': successful_recommendations,
                    'total_recommendations': total_recommendations
                }
            }
            
            print(f"    ✓ KNN Recommender: {accuracy:.2f}% accuracy")
            
        except Exception as e:
            print(f"    ✗ KNN Recommender: Error - {str(e)}")
            results = {
                'KNN Recommender': {
                    'accuracy': 0,
                    'successful_recommendations': 0,
                    'total_recommendations': 0
                }
            }
        
        return results
    
    def test_user_preference_models(self, user_data):
        """Test user preference prediction models."""
        print("\n👤 Testing User Preference Models...")
        
        # Split data for training and testing
        train_size = int(len(user_data) * 0.8)
        train_data = user_data[:train_size]
        test_data = user_data[train_size:]
        
        models = {
            'Basic Random Forest': UserPreferenceModel(),
            'Improved Random Forest': ImprovedUserPreferenceModel(n_trials=10)  # Reduced trials for speed
        }
        
        results = {}
        
        for model_name, model in models.items():
            try:
                print(f"  Testing {model_name}...")
                
                # Save data to temporary files
                train_file = 'temp_train_users.json'
                test_file = 'temp_test_users.json'
                
                with open(train_file, 'w') as f:
                    json.dump(train_data, f)
                with open(test_file, 'w') as f:
                    json.dump(test_data, f)
                
                # Train model
                if isinstance(model, ImprovedUserPreferenceModel):
                    model.train(train_file, use_cross_validation=False)  # Disable CV for speed
                else:
                    model.train(train_file)
                
                # Evaluate model
                report = model.evaluate(test_file)
                
                # Extract accuracy from classification report
                lines = report.split('\n')
                accuracy_line = [line for line in lines if 'accuracy' in line.lower()]
                if accuracy_line:
                    accuracy = float(accuracy_line[0].split()[-1]) * 100
                else:
                    accuracy = 0
                
                results[model_name] = {
                    'accuracy': accuracy,
                    'report': report
                }
                
                print(f"    ✓ {model_name}: {accuracy:.2f}% accuracy")
                
                # Clean up temporary files
                import os
                if os.path.exists(train_file):
                    os.remove(train_file)
                if os.path.exists(test_file):
                    os.remove(test_file)
                
            except Exception as e:
                print(f"    ✗ {model_name}: Error - {str(e)}")
                results[model_name] = {
                    'accuracy': 0,
                    'report': f"Error: {str(e)}"
                }
        
        return results
    
    def create_visualizations(self):
        """Create comprehensive visualizations of model accuracy."""
        print("\n📊 Creating visualizations...")
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('ThriftCart Model Accuracy Comparison', fontsize=16, fontweight='bold')
        
        # 1. Price Prediction Models
        if 'price_prediction' in self.results:
            price_data = self.results['price_prediction']
            models = list(price_data.keys())
            accuracies = [price_data[model]['accuracy'] for model in models]
            
            bars1 = ax1.bar(models, accuracies, color='skyblue', alpha=0.7)
            ax1.set_title('Price Prediction Models', fontweight='bold')
            ax1.set_ylabel('Accuracy (%)')
            ax1.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar, acc in zip(bars1, accuracies):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            ax1.tick_params(axis='x', rotation=45)
        
        # 2. Sentiment Analysis Models
        if 'sentiment_analysis' in self.results:
            sentiment_data = self.results['sentiment_analysis']
            models = list(sentiment_data.keys())
            accuracies = [sentiment_data[model]['accuracy'] for model in models]
            
            bars2 = ax2.bar(models, accuracies, color='lightcoral', alpha=0.7)
            ax2.set_title('Sentiment Analysis Models', fontweight='bold')
            ax2.set_ylabel('Accuracy (%)')
            ax2.set_ylim(0, 100)
            
            for bar, acc in zip(bars2, accuracies):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            ax2.tick_params(axis='x', rotation=45)
        
        # 3. Recommendation Model
        if 'recommendation' in self.results:
            rec_data = self.results['recommendation']
            models = list(rec_data.keys())
            accuracies = [rec_data[model]['accuracy'] for model in models]
            
            bars3 = ax3.bar(models, accuracies, color='lightgreen', alpha=0.7)
            ax3.set_title('Recommendation Models', fontweight='bold')
            ax3.set_ylabel('Accuracy (%)')
            ax3.set_ylim(0, 100)
            
            for bar, acc in zip(bars3, accuracies):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            ax3.tick_params(axis='x', rotation=45)
        
        # 4. User Preference Models
        if 'user_preference' in self.results:
            pref_data = self.results['user_preference']
            models = list(pref_data.keys())
            accuracies = [pref_data[model]['accuracy'] for model in models]
            
            bars4 = ax4.bar(models, accuracies, color='gold', alpha=0.7)
            ax4.set_title('User Preference Models', fontweight='bold')
            ax4.set_ylabel('Accuracy (%)')
            ax4.set_ylim(0, 100)
            
            for bar, acc in zip(bars4, accuracies):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
                        f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        self.figures['accuracy_comparison'] = fig
        
        # Create overall comparison chart
        fig2, ax = plt.subplots(figsize=(12, 8))
        
        all_models = []
        all_accuracies = []
        categories = []
        
        for category, data in self.results.items():
            for model, metrics in data.items():
                if 'accuracy' in metrics:
                    all_models.append(f"{category}\n{model}")
                    all_accuracies.append(metrics['accuracy'])
                    categories.append(category)
        
        # Color code by category
        colors = {'price_prediction': 'skyblue', 'sentiment_analysis': 'lightcoral', 
                 'recommendation': 'lightgreen', 'user_preference': 'gold'}
        bar_colors = [colors.get(cat, 'gray') for cat in categories]
        
        bars = ax.bar(all_models, all_accuracies, color=bar_colors, alpha=0.7)
        ax.set_title('Overall Model Accuracy Comparison', fontsize=14, fontweight='bold')
        ax.set_ylabel('Accuracy (%)')
        ax.set_ylim(0, 100)
        
        # Add value labels
        for bar, acc in zip(bars, all_accuracies):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        self.figures['overall_comparison'] = fig2
        
        return self.figures
    
    def print_detailed_results(self):
        """Print detailed results for each model category."""
        print("\n" + "="*80)
        print("📋 DETAILED MODEL ACCURACY RESULTS")
        print("="*80)
        
        for category, data in self.results.items():
            print(f"\n🔍 {category.upper().replace('_', ' ')}")
            print("-" * 50)
            
            for model, metrics in data.items():
                print(f"\n📊 {model}:")
                for metric, value in metrics.items():
                    if metric != 'report':  # Skip detailed reports in summary
                        if isinstance(value, float):
                            print(f"   {metric}: {value:.2f}")
                        else:
                            print(f"   {metric}: {value}")
                
                # Print classification report if available
                if 'report' in metrics and metrics['report']:
                    print(f"   Detailed Report:\n{metrics['report']}")
        
        # Print summary statistics
        print("\n" + "="*80)
        print("📈 SUMMARY STATISTICS")
        print("="*80)
        
        all_accuracies = []
        for category, data in self.results.items():
            for model, metrics in data.items():
                if 'accuracy' in metrics:
                    all_accuracies.append(metrics['accuracy'])
        
        if all_accuracies:
            print(f"Average Accuracy: {np.mean(all_accuracies):.2f}%")
            print(f"Best Accuracy: {np.max(all_accuracies):.2f}%")
            print(f"Worst Accuracy: {np.min(all_accuracies):.2f}%")
            print(f"Standard Deviation: {np.std(all_accuracies):.2f}%")
    
    def run_comparison(self):
        """Run the complete model accuracy comparison."""
        print("🚀 Starting ThriftCart Model Accuracy Comparison")
        print("="*60)
        
        # Generate test data
        test_data = self.generate_synthetic_data(n_samples=500)  # Reduced for speed
        
        # Test all model categories
        self.results['price_prediction'] = self.test_price_prediction_models(test_data['price_data'])
        self.results['sentiment_analysis'] = self.test_sentiment_analysis_models(test_data['reviews'])
        self.results['recommendation'] = self.test_recommendation_model(test_data['user_data'])
        self.results['user_preference'] = self.test_user_preference_models(test_data['user_data'])
        
        # Create visualizations
        self.create_visualizations()
        
        # Print detailed results
        self.print_detailed_results()
        
        # Save results
        self.save_results()
        
        print("\n✅ Model accuracy comparison completed!")
        print("📁 Results saved to 'model_accuracy_results.json'")
        print("📊 Visualizations saved to 'model_accuracy_plots.png'")
        
        return self.results, self.figures
    
    def save_results(self):
        """Save results to files."""
        # Save JSON results
        with open('model_accuracy_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Save plots
        for name, fig in self.figures.items():
            fig.savefig(f'model_accuracy_{name}.png', dpi=300, bbox_inches='tight')
        
        # Save combined plot
        if 'overall_comparison' in self.figures:
            self.figures['overall_comparison'].savefig('model_accuracy_comparison.png', dpi=300, bbox_inches='tight')

def main():
    """Main function to run the model accuracy comparison."""
    try:
        # Initialize comparison
        comparison = ModelAccuracyComparison()
        
        # Run comparison
        results, figures = comparison.run_comparison()
        
        # Display plots
        plt.show()
        
    except Exception as e:
        print(f"❌ Error during model comparison: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 