import re
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Union, Optional
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import joblib
import os
from datetime import datetime

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('omw-1.4')

class SentimentAnalyzer:
    """
    A class for performing sentiment analysis on product reviews.
    Supports TextBlob and VADER analysis methods.
    """
    
    def __init__(self, method: str = 'vader', use_gpu: bool = False):
        """
        Initialize the SentimentAnalyzer.
        Args:
            method (str): Sentiment analysis method to use. 
                         Options: 'textblob', 'vader'
            use_gpu (bool): Ignored, for compatibility only.
        """
        self.method = method.lower()
        self.analyzer = None
        self.aspects = None
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.last_trained = None
        self.is_fitted = False
        
        # Initialize the appropriate sentiment analyzer
        if self.method == 'textblob':
            pass  # TextBlob is used on the fly
        elif self.method == 'vader':
            self.analyzer = SentimentIntensityAnalyzer()
        else:
            raise ValueError(f"Unsupported sentiment analysis method: {method}")
    
    def _preprocess_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'<.*?>', '', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        words = word_tokenize(text)
        words = [self.lemmatizer.lemmatize(word) for word in words if word not in self.stop_words]
        return ' '.join(words)
    
    def _analyze_sentiment_textblob(self, text: str) -> Dict[str, float]:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': sentiment,
            'positive': (polarity + 1) / 2,
            'negative': (-polarity + 1) / 2,
            'neutral': 1 - abs(polarity)
        }
    
    def _analyze_sentiment_vader(self, text: str) -> Dict[str, float]:
        scores = self.analyzer.polarity_scores(text)
        if scores['compound'] >= 0.05:
            sentiment = 'positive'
        elif scores['compound'] <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        return {
            **scores,
            'sentiment': sentiment
        }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Union[str, float]]:
        if self.method == 'textblob':
            return self._analyze_sentiment_textblob(text)
        elif self.method == 'vader':
            return self._analyze_sentiment_vader(text)
        else:
            raise ValueError(f"Unsupported sentiment analysis method: {self.method}")
    
    # The rest of the class (aspect extraction, batch analysis, etc.) can be added as needed, but must not use transformers.
