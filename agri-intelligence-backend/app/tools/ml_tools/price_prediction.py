"""
Market Price Prediction ML Tool
Predicts commodity prices using time series analysis
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import joblib
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class PricePredictionTool:
    def __init__(self):
        self.models = {}
        self.feature_window = 30  # Use last 30 days for prediction
        
    def train_price_model(self, commodity: str, price_data: pd.DataFrame) -> Dict:
        """Train price prediction model for specific commodity"""
        try:
            # Prepare time series features
            price_data = price_data.sort_values('date')
            price_data['price_lag_1'] = price_data['modal_price'].shift(1)
            price_data['price_lag_7'] = price_data['modal_price'].shift(7)
            price_data['price_ma_7'] = price_data['modal_price'].rolling(7).mean()
            price_data['price_ma_30'] = price_data['modal_price'].rolling(30).mean()
            price_data['price_volatility'] = price_data['modal_price'].rolling(7).std()
            
            # Create seasonal features
            price_data['month'] = pd.to_datetime(price_data['date']).dt.month
            price_data['day_of_year'] = pd.to_datetime(price_data['date']).dt.dayofyear
            
            # Remove rows with NaN values
            price_data = price_data.dropna()
            
            # Features and target
            feature_cols = ['price_lag_1', 'price_lag_7', 'price_ma_7', 'price_ma_30', 
                          'price_volatility', 'month', 'day_of_year']
            X = price_data[feature_cols]
            y = price_data['modal_price']
            
            # Train Random Forest model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Store model
            self.models[commodity] = {
                'model': model,
                'feature_columns': feature_cols,
                'last_training_date': datetime.now().isoformat()
            }
            
            # Evaluate model
            y_pred = model.predict(X)
            mae = mean_absolute_error(y, y_pred)
            
            return {
                'commodity': commodity,
                'model_type': 'Random Forest',
                'mean_absolute_error': mae,
                'training_samples': len(X),
                'feature_importance': dict(zip(feature_cols, model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Price model training error: {e}")
            return {'error': str(e)}

    def predict_price(self, commodity: str, current_market_data: Dict, 
                     prediction_days: int = 7) -> Dict:
        """Predict prices for next N days"""
        try:
            if commodity not in self.models:
                return {'error': f'No trained model found for {commodity}'}
            
            model_info = self.models[commodity]
            model = model_info['model']
            
            # Prepare current features
            current_features = self._prepare_features(current_market_data)
            
            # Make predictions
            predictions = []
            for day in range(1, prediction_days + 1):
                # Predict next day price
                predicted_price = model.predict([current_features])[0]
                
                future_date = datetime.now() + timedelta(days=day)
                predictions.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_price': round(predicted_price, 2),
                    'confidence': self._calculate_price_confidence(current_market_data),
                    'trend': self._analyze_trend(predicted_price, current_market_data.get('current_price', 0))
                })
                
                # Update features for next iteration
                current_features = self._update_features(current_features, predicted_price)
            
            return {
                'commodity': commodity,
                'predictions': predictions,
                'recommendation': self._generate_price_recommendation(predictions, commodity)
            }
            
        except Exception as e:
            logger.error(f"Price prediction error: {e}")
            return {'error': str(e)}

    def _prepare_features(self, market_data: Dict) -> List[float]:
        """Prepare features for price prediction"""
        return [
            market_data.get('current_price', 3000),  # price_lag_1
            market_data.get('price_week_ago', 3000),  # price_lag_7
            market_data.get('price_ma_7', 3000),     # price_ma_7
            market_data.get('price_ma_30', 3000),    # price_ma_30
            market_data.get('price_volatility', 100), # price_volatility
            datetime.now().month,                     # month
            datetime.now().timetuple().tm_yday       # day_of_year
        ]
    
    def _update_features(self, features: List[float], new_price: float) -> List[float]:
        """Update features with new predicted price"""
        # Simple feature update (in production, use proper time series handling)
        features[0] = new_price  # Update price_lag_1
        return features
    
    def _calculate_price_confidence(self, market_data: Dict) -> str:
        """Calculate prediction confidence"""
        volatility = market_data.get('price_volatility', 100)
        
        if volatility < 50:
            return "High"
        elif volatility < 150:
            return "Medium"
        else:
            return "Low"
    
    def _analyze_trend(self, predicted_price: float, current_price: float) -> str:
        """Analyze price trend"""
        if predicted_price > current_price * 1.02:
            return "Increasing"
        elif predicted_price < current_price * 0.98:
            return "Decreasing"
        else:
            return "Stable"
    
    def _generate_price_recommendation(self, predictions: List[Dict], commodity: str) -> str:
        """Generate trading recommendation based on predictions"""
        if not predictions:
            return f"Unable to generate recommendation for {commodity}"
        
        current_price = predictions[0].get('predicted_price', 0)
        week_price = predictions[-1].get('predicted_price', 0) if len(predictions) >= 7 else current_price
        
        price_change = ((week_price - current_price) / current_price) * 100
        
        if price_change > 5:
            return f"Hold {commodity}. Prices expected to increase by {price_change:.1f}%"
        elif price_change < -5:
            return f"Consider selling {commodity} soon. Prices may decrease by {abs(price_change):.1f}%"
        else:
            return f"{commodity} prices likely to remain stable. Monitor daily for changes."

# Global price prediction tool instance
price_tool = PricePredictionTool()
