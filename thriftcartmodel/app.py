import os
import json
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import config

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load user data
with open(config.USER_DATA_FILE, 'r') as f:
    users_data = json.load(f)

# Convert to DataFrame for easier manipulation
users_df = pd.json_normalize(users_data)

@app.route('/')
def index():
    return jsonify({
        'message': 'Welcome to BestPickr API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route(f'{config.API_PREFIX}/users', methods=['GET'])
def get_users():
    """Get list of all users"""
    return jsonify(users_data)

@app.route(f'{config.API_PREFIX}/recommendations/<user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Get personalized recommendations for a user"""
    # TODO: Implement recommendation logic
    return jsonify({
        'user_id': user_id,
        'recommendations': [],
        'message': 'Recommendation endpoint - implementation pending'
    })

@app.route(f'{config.API_PREFIX}/compare', methods=['POST'])
def compare_products():
    """Compare products across platforms"""
    data = request.get_json()
    # TODO: Implement comparison logic
    return jsonify({
        'status': 'success',
        'comparison': [],
        'message': 'Comparison endpoint - implementation pending'
    })

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0', port=5000)
