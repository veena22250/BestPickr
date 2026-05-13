# ThrifCart - Smart Product Comparison Platform

ThrifCart is an intelligent product comparison application that helps users find the best deals across multiple platforms and categories. The application uses machine learning to provide personalized recommendations, price predictions, and sentiment analysis.

## Features

1. **Multi-Platform Product Comparison**
   - Grocery apps (Blinkit, Zomato, Swiggy, Dunzo, Zepto, BigB, More, Jiomart)
   - Ride services (Ola, Uber, Namma Yatri, Rapido)
   - E-commerce platforms (Myntra, Ajio, Flipkart, Meesho, Amazon)

2. **Personalized Recommendations**
   - KNN-based product recommendations
   - User preference modeling
   - Collaborative filtering

3. **Price Trend Analysis**
   - ARIMA-based price prediction
   - "Buy now or wait?" insights
   - Historical price tracking

4. **Sentiment Analysis**
   - Review summarization
   - Sentiment-based product scoring
   - Aspect-based sentiment analysis

5. **Chatbot Integration**
   - Rule-based product queries
   - Cart management
   - Platform comparison

## Project Structure

```
thriftcart/
├── app/                      # Main application package
│   ├── __init__.py
│   ├── models/               # ML models
│   │   ├── __init__.py
│   │   ├── recommendation.py # KNN recommender
│   │   ├── price_predictor.py # ARIMA model
│   │   └── sentiment.py      # Sentiment analysis
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── comparison.py     # Price comparison logic
│   │   └── chatbot.py        # Chatbot implementation
│   └── utils/                # Utility functions
│       ├── __init__.py
│       ├── data_loader.py    # Data loading utilities
│       └── preprocessor.py   # Data preprocessing
├── data/                     # Data storage
│   ├── raw/                  # Raw data files
│   └── processed/            # Processed data files
├── static/                   # Static files (CSS, JS, images)
│   ├── css/
│   └── js/
├── templates/                # HTML templates
├── tests/                    # Unit tests
├── config.py                 # Configuration settings
├── app.py                    # Main application entry point
└── requirements.txt          # Project dependencies
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python app.py
   ```

## Data Generation

To generate synthetic data for testing and development:

```bash
python -m data.generate_data
```

## API Documentation

API documentation is available at `/docs` when the application is running locally.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
