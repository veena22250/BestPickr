import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Data paths
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
MODEL_DIR = BASE_DIR / 'models'

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODEL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application settings
class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Model settings
    KNN_NEIGHBORS = 5
    ARIMA_ORDER = (1, 1, 1)  # (p, d, q) for ARIMA
    
    # API settings
    API_PREFIX = '/api/v1'
    
    # Sentiment analysis settings
    SENTIMENT_MODEL = 'distilbert-base-uncased-finetuned-sst-2-english'
    
    # Data file paths
    USER_DATA_FILE = str(RAW_DATA_DIR / 'synthetic_users_50.json')
    
    # Platform configurations
    PLATFORMS = {
        'grocery': ['blinkit', 'zomato', 'swiggy', 'dunzo', 'zepto', 'bigb', 'more', 'jiomart'],
        'ride': ['ola', 'uber', 'namma_yatri', 'rapido'],
        'ecommerce': ['myntra', 'ajio', 'flipkart', 'meesho', 'amazon']
    }

# Initialize config
config = Config()
