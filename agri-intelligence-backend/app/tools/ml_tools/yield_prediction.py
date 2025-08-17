"""
Crop Yield Prediction ML Tool
Uses historical data and weather patterns to predict crop yields
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class YieldPredictionTool:
    def __init__(self):
        self.model = None
        self.feature_columns = [
            'rainfall', 'temperature', 'humidity', 'soil_ph', 
            'fertilizer_npk_ratio', 'irrigation_type', 'seed_variety',
            'sowing_month', 'area_hectares'
        ]
        
    def train_model(self, training_data: pd.DataFrame) -> Dict:
        """Train yield prediction model on historical data"""
        try:
            # Prepare features and target
            X = training_data[self.feature_columns]
            y = training_data['yield_kg_per_ha']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Train Gradient Boosting model
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model
            joblib.dump(self.model, 'yield_prediction_model.pkl')
            
            return {
                'model_type': 'Gradient Boosting',
                'mean_absolute_error': mae,
                'r2_score': r2,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return {'error': str(e)}

    def predict_yield(self, farm_data: Dict) -> Dict:
        """Predict crop yield for given farm conditions"""
        try:
            if not self.model:
                # Load pre-trained model
                self.model = joblib.load('yield_prediction_model.pkl')
            
            # Prepare input features
            features = np.array([[
                farm_data.get('rainfall', 800),
                farm_data.get('temperature', 25),
                farm_data.get('humidity', 65),
                farm_data.get('soil_ph', 6.5),
                farm_data.get('fertilizer_npk_ratio', 1.5),
                self._encode_irrigation_type(farm_data.get('irrigation_type', 'canal')),
                self._encode_seed_variety(farm_data.get('seed_variety', 'local')),
                farm_data.get('sowing_month', 6),
                farm_data.get('area_hectares', 1.0)
            ]])
            
            # Make prediction
            predicted_yield = self.model.predict(features)[0]
            
            # Calculate confidence intervals
            confidence = self._calculate_confidence(farm_data)
            
            return {
                'predicted_yield_kg_per_ha': round(predicted_yield, 2),
                'confidence_level': confidence,
                'yield_category': self._categorize_yield(predicted_yield),
                'recommendations': self._generate_yield_recommendations(predicted_yield, farm_data)
            }
            
        except Exception as e:
            logger.error(f"Yield prediction error: {e}")
            return {'error': str(e)}

    def _encode_irrigation_type(self, irrigation_type: str) -> float:
        """Encode irrigation type to numerical value"""
        encoding = {
            'drip': 1.0, 'sprinkler': 0.8, 'canal': 0.6, 
            'well': 0.7, 'rainfed': 0.3
        }
        return encoding.get(irrigation_type.lower(), 0.5)
    
    def _encode_seed_variety(self, seed_variety: str) -> float:
        """Encode seed variety to numerical value"""
        encoding = {
            'hybrid': 1.0, 'improved': 0.8, 'local': 0.6, 'traditional': 0.4
        }
        return encoding.get(seed_variety.lower(), 0.6)
    
    def _calculate_confidence(self, farm_data: Dict) -> str:
        """Calculate prediction confidence based on data quality"""
        data_quality_score = 0
        total_factors = 0
        
        # Check data completeness and quality
        if farm_data.get('rainfall') and 200 <= farm_data['rainfall'] <= 2000:
            data_quality_score += 1
        total_factors += 1
        
        if farm_data.get('temperature') and 15 <= farm_data['temperature'] <= 40:
            data_quality_score += 1
        total_factors += 1
        
        if farm_data.get('soil_ph') and 5.5 <= farm_data['soil_ph'] <= 8.5:
            data_quality_score += 1
        total_factors += 1
        
        confidence_ratio = data_quality_score / total_factors
        
        if confidence_ratio >= 0.8:
            return "High"
        elif confidence_ratio >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _categorize_yield(self, yield_value: float) -> str:
        """Categorize yield as Low, Medium, or High"""
        if yield_value >= 4000:
            return "High Yield"
        elif yield_value >= 2500:
            return "Medium Yield"
        else:
            return "Low Yield"
    
    def _generate_yield_recommendations(self, predicted_yield: float, farm_data: Dict) -> List[str]:
        """Generate recommendations to improve yield"""
        recommendations = []
        
        if predicted_yield < 3000:
            recommendations.append("Consider using improved seed varieties")
            recommendations.append("Optimize fertilizer application based on soil testing")
            
        if farm_data.get('irrigation_type') == 'rainfed':
            recommendations.append("Install drip or sprinkler irrigation system")
            
        if farm_data.get('soil_ph', 7) < 6.0:
            recommendations.append("Apply lime to improve soil pH")
            
        if not recommendations:
            recommendations.append("Continue current practices for optimal yield")
            
        return recommendations

# Global yield prediction tool instance
yield_tool = YieldPredictionTool()
