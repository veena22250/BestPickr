import joblib
import numpy as np

# Load the trained model and encoders
model = joblib.load('models/user_preference_model.joblib')
encoders = joblib.load('models/encoders.joblib')

# Sample user data (modify these values to test different scenarios)
sample_user = {
    'age': 30,
    'gender': 'female',
    'location': 'New York',
    'price_sensitivity': 'medium',
    'discount_preference': 1,  # 1 for True, 0 for False
    'delivery_speed': 'standard',
    'order_size': '2-3 people'
}

def preprocess_user(user_data, encoders):
    """Preprocess user data for prediction."""
    # Create a copy to avoid modifying the original
    user = user_data.copy()
    
    # Encode categorical variables
    for col in ['gender', 'location', 'price_sensitivity', 'delivery_speed', 'order_size']:
        le = encoders[col]
        # Handle unseen labels
        if user[col] not in le.classes_:
            print(f"Warning: {col} value '{user[col]}' not seen during training. Using default value.")
            user[col] = le.classes_[0]  # Use first category as default
        user[col] = le.transform([user[col]])[0]
    
    # Convert to numpy array in the correct feature order
    features = ['age', 'gender', 'location', 'price_sensitivity', 
               'discount_preference', 'delivery_speed', 'order_size']
    
    return np.array([[user[col] for col in features]])

# Make a prediction
preprocessed_data = preprocess_user(sample_user, encoders)
prediction_encoded = model.predict(preprocessed_data)[0]
predicted_category = encoders['target_encoder'].inverse_transform([prediction_encoded])[0]

# Get prediction probabilities
probabilities = model.predict_proba(preprocessed_data)[0]
category_probabilities = {}
for i, prob in enumerate(probabilities):
    category = encoders['target_encoder'].classes_[i]
    category_probabilities[category] = f"{prob*100:.1f}%"

# Print results
print("\n=== Model Prediction ===")
print(f"Input User: {sample_user}")
print(f"\nPredicted Category: {predicted_category}")
print("\nPrediction Probabilities:")
for category, prob in sorted(category_probabilities.items(), key=lambda x: float(x[1].rstrip('%')), reverse=True):
    print(f"- {category}: {prob}")

# Print feature importance if available
if hasattr(model, 'feature_importances_'):
    print("\nFeature Importances:")
    features = ['age', 'gender', 'location', 'price_sensitivity', 
               'discount_preference', 'delivery_speed', 'order_size']
    for feature, importance in zip(features, model.feature_importances_):
        print(f"- {feature}: {importance*100:.1f}%")
