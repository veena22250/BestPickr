import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union, Optional
import warnings
from config import config

# Suppress warnings
warnings.filterwarnings('ignore')

class PricePredictor:
    """ 
    A class for predicting price trends using various models including ARIMA and tree-based methods.
    """
    
    def __init__(self, model_type: str = 'arima'):
        """
        Initialize the PricePredictor.
        
        Args:
            model_type (str): Type of model to use. Options: 'arima', 'sarima', 'random_forest', 'xgboost', 'lightgbm', 'catboost'
        """
        self.model_type = model_type.lower()
        self.model = None
        self.last_trained = None
        self.scaler = None
        self.feature_columns = None
        self.target_column = 'price'
        self.is_fitted = False
        
        # Model-specific parameters
        self.model_params = {
            'arima': {'order': (1, 1, 1)},  # Default ARIMA order (p,d,q)
            'sarima': {'order': (1, 1, 1), 'seasonal_order': (1, 1, 1, 7)},  # Weekly seasonality
            'random_forest': {'n_estimators': 100, 'random_state': 42},
            'xgboost': {'n_estimators': 100, 'learning_rate': 0.1, 'random_state': 42},
            'lightgbm': {'n_estimators': 100, 'learning_rate': 0.1, 'random_state': 42},
            'catboost': {'iterations': 100, 'learning_rate': 0.1, 'random_state': 42}
        }
    
    def _prepare_time_series_data(self, data: pd.DataFrame, date_col: str, value_col: str, 
                                freq: str = 'D') -> pd.Series:
        """
        Prepare time series data for modeling.
        
        Args:
            data: DataFrame containing the time series data
            date_col: Name of the date column
            value_col: Name of the value column to predict
            freq: Frequency of the time series ('D' for daily, 'H' for hourly, etc.)
            
        Returns:
            pd.Series: Time series data with datetime index
        """
        # Convert date column to datetime and set as index
        ts = data.copy()
        ts[date_col] = pd.to_datetime(ts[date_col])
        ts = ts.set_index(date_col)[value_col]
        
        # Resample to ensure consistent frequency and forward fill missing values
        ts = ts.asfreq(freq).ffill()
        
        return ts
    
    def _create_features(self, data: pd.Series, lags: int = 7) -> pd.DataFrame:
        """
        Create time series features for machine learning models.
        
        Args:
            data: Time series data
            lags: Number of lag features to create
            
        Returns:
            pd.DataFrame: DataFrame with features and target
        """
        df = pd.DataFrame()
        df['value'] = data
        
        # Create lag features
        for i in range(1, lags + 1):
            df[f'lag_{i}'] = df['value'].shift(i)
        
        # Create date-based features
        df['day'] = df.index.day
        df['month'] = df.index.month
        df['year'] = df.index.year
        df['dayofweek'] = df.index.dayofweek
        df['quarter'] = df.index.quarter
        df['dayofyear'] = df.index.dayofyear
        df['weekofyear'] = df.index.weekofyear
        
        # Drop rows with NaN values from lag features
        df = df.dropna()
        
        return df
    
    def fit(self, data: Union[pd.DataFrame, pd.Series], date_col: str = None, 
            value_col: str = None, **kwargs) -> 'PricePredictor':
        """
        Fit the price prediction model.
        
        Args:
            data: Time series data (DataFrame with date and value columns, or Series with datetime index)
            date_col: Name of the date column (if data is a DataFrame)
            value_col: Name of the value column (if data is a DataFrame)
            **kwargs: Additional model-specific parameters
            
        Returns:
            self: Fitted model instance
        """
        # Prepare time series data
        if isinstance(data, pd.DataFrame) and date_col and value_col:
            ts = self._prepare_time_series_data(data, date_col, value_col)
        elif isinstance(data, pd.Series):
            ts = data.copy()
            if not isinstance(ts.index, pd.DatetimeIndex):
                raise ValueError("Series must have a DatetimeIndex")
        else:
            raise ValueError("Invalid input data format. Provide either a DataFrame with date_col and value_col or a Series with DatetimeIndex.")
        
        # Update model parameters with any provided kwargs
        if self.model_type in self.model_params:
            self.model_params[self.model_type].update(kwargs)
        
        # Fit the appropriate model
        if self.model_type == 'arima':
            order = self.model_params['arima'].get('order', (1, 1, 1))
            self.model = ARIMA(ts, order=order).fit()
            
        elif self.model_type == 'sarima':
            order = self.model_params['sarima'].get('order', (1, 1, 1))
            seasonal_order = self.model_params['sarima'].get('seasonal_order', (1, 1, 1, 7))
            self.model = SARIMAX(ts, order=order, seasonal_order=seasonal_order).fit(disp=False)
            
        else:  # Tree-based models
            # Create features for machine learning
            df_features = self._create_features(ts, lags=7)
            X = df_features.drop('value', axis=1)
            y = df_features['value']
            
            # Store feature columns for later use
            self.feature_columns = X.columns.tolist()
            
            # Initialize and fit the model
            if self.model_type == 'random_forest':
                self.model = RandomForestRegressor(**self.model_params['random_forest'])
            elif self.model_type == 'xgboost':
                self.model = XGBRegressor(**self.model_params['xgboost'])
            elif self.model_type == 'lightgbm':
                self.model = LGBMRegressor(**self.model_params['lightgbm'])
            elif self.model_type == 'catboost':
                self.model = CatBoostRegressor(**self.model_params['catboost'], verbose=0)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
                
            self.model.fit(X, y)
        
        self.last_trained = datetime.now()
        self.is_fitted = True
        return self
    
    def predict(self, steps: int = 7, X: Optional[pd.DataFrame] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict future values.
        
        Args:
            steps: Number of steps ahead to forecast
            X: Feature matrix for tree-based models (only needed for some model types)
            
        Returns:
            tuple: (predictions, confidence_intervals)
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        
        if self.model_type in ['arima', 'sarima']:
            # Get predictions with confidence intervals
            forecast = self.model.get_forecast(steps=steps)
            predictions = forecast.predicted_mean.values
            conf_int = forecast.conf_int().values
            
            return predictions, conf_int
            
        else:  # Tree-based models
            if X is None:
                raise ValueError(f"Feature matrix X is required for {self.model_type} model")
                
            if not set(self.feature_columns).issubset(X.columns):
                raise ValueError(f"Feature matrix must contain columns: {self.feature_columns}")
                
            X = X[self.feature_columns]
            predictions = self.model.predict(X)
            
            # For tree-based models, we don't have built-in confidence intervals
            # You could implement bootstrapping or use quantile regression for this
            conf_int = None
            
            return predictions, conf_int
    
    def evaluate(self, test_data: pd.Series, metric: str = 'mae') -> float:
        """
        Evaluate the model on test data.
        
        Args:
            test_data: Test time series data
            metric: Evaluation metric ('mae', 'mse', 'rmse')
            
        Returns:
            float: Evaluation score
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
            
        if self.model_type in ['arima', 'sarima']:
            # For time series models, we can use the built-in evaluation
            pred = self.model.predict(start=test_data.index[0], end=test_data.index[-1])
            actual = test_data
            
        else:  # Tree-based models
            # Create features for the test data
            df_features = self._create_features(test_data)
            X_test = df_features.drop('value', axis=1)
            y_test = df_features['value']
            
            pred = self.model.predict(X_test)
            actual = y_test
        
        # Calculate the specified metric
        if metric.lower() == 'mae':
            score = mean_absolute_error(actual, pred)
        elif metric.lower() == 'mse':
            score = mean_squared_error(actual, pred)
        elif metric.lower() == 'rmse':
            score = np.sqrt(mean_squared_error(actual, pred))
        else:
            raise ValueError(f"Unsupported metric: {metric}")
            
        return score
    
    def get_buy_recommendation(self, current_price: float, predicted_prices: np.ndarray, 
                             confidence_intervals: np.ndarray = None, 
                             threshold: float = 0.05) -> Dict[str, Union[bool, str, float]]:
        """
        Generate a 'Buy now or wait?' recommendation based on price predictions.
        
        Args:
            current_price: Current price of the product
            predicted_prices: Array of predicted future prices
            confidence_intervals: Array of confidence intervals for the predictions
            threshold: Price change threshold to trigger a recommendation (default: 5%)
            
        Returns:
            dict: Recommendation details
        """
        if len(predicted_prices) == 0:
            return {
                'recommendation': 'insufficient_data',
                'message': 'Not enough data to make a recommendation',
                'confidence': 0.0
            }
        
        # Calculate expected price change
        avg_predicted_price = np.mean(predicted_prices)
        price_change = (avg_predicted_price - current_price) / current_price
        
        # Determine recommendation
        if price_change > threshold:
            recommendation = 'buy_now'
            message = f'Prices are expected to increase by {price_change*100:.1f}%'
        elif price_change < -threshold:
            recommendation = 'wait'
            message = f'Prices are expected to decrease by {-price_change*100:.1f}%'
        else:
            recommendation = 'neutral'
            message = 'Prices are expected to remain stable'
        
        # Calculate confidence (simplified)
        if confidence_intervals is not None:
            # Calculate the width of the confidence interval relative to the predicted value
            ci_width = (confidence_intervals[:, 1] - confidence_intervals[:, 0]) / predicted_prices
            confidence = 1.0 - np.mean(ci_width)  # Narrower CI = higher confidence
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        else:
            confidence = 0.7  # Default confidence if no CI is provided
        
        return {
            'recommendation': recommendation,
            'message': message,
            'current_price': current_price,
            'predicted_price': avg_predicted_price,
            'price_change_pct': price_change * 100,
            'confidence': confidence
        }
    
    def save(self, filepath: str) -> None:
        """
        Save the model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Nothing to save.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save model and metadata
        model_data = {
            'model_type': self.model_type,
            'model': self.model,
            'last_trained': self.last_trained,
            'feature_columns': self.feature_columns,
            'model_params': self.model_params
        }
        
        joblib.dump(model_data, filepath)
    
    @classmethod
    def load(cls, filepath: str) -> 'PricePredictor':
        """
        Load a saved model from disk.
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            PricePredictor: Loaded model instance
        """
        model_data = joblib.load(filepath)
        
        # Create new predictor instance
        predictor = cls(model_type=model_data['model_type'])
        
        # Restore attributes
        predictor.model = model_data['model']
        predictor.last_trained = model_data['last_trained']
        predictor.feature_columns = model_data['feature_columns']
        predictor.model_params = model_data['model_params']
        predictor.is_fitted = True
        
        return predictor
