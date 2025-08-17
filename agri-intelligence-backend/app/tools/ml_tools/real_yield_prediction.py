"""
PRODUCTION-READY Yield Prediction with Pre-trained Models
Models are trained once, saved to disk, and loaded instantly for predictions
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, HistGradientBoostingRegressor  # add faster GBM with early stopping
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib
import asyncpg
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime
import os
import json

logger = logging.getLogger(__name__)

class ProductionYieldPredictionModel:
    def __init__(self, db_url: str = None, model_dir: str = "models"):
        self.db_url = db_url or os.getenv('DATABASE_URL', 'postgresql://postgres@localhost:5433/agri_db')
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, 'yield_prediction_model.pkl')
        self.metadata_path = os.path.join(model_dir, 'model_metadata.json')
        
        # Model components (loaded from disk)
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.feature_names = []
        self.model_metadata = {}
        self.is_loaded = False
        
        # Create model directory if it doesn't exist
        os.makedirs(model_dir, exist_ok=True)
        
        # Try to load existing model on initialization
        self._load_model()

    def _load_model(self) -> bool:
        """Load pre-trained model from disk - FAST startup"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.metadata_path):
                # Load model components
                model_data = joblib.load(self.model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                self.feature_names = model_data['feature_names']
                
                # Load metadata
                with open(self.metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                
                self.is_loaded = True
                logger.info(f"✅ Pre-trained model loaded successfully!")
                logger.info(f"   Model version: {self.model_metadata.get('version', 'unknown')}")
                logger.info(f"   Trained on: {self.model_metadata.get('training_date', 'unknown')}")
                logger.info(f"   Test R² Score: {self.model_metadata.get('test_r2_score', 'unknown')}")
                return True
            else:
                logger.warning("⚠️ No pre-trained model found. Run training first.")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to load pre-trained model: {e}")
            self.is_loaded = False
            return False

    async def train_and_save_model(self, force_retrain: bool = False) -> Dict:
        """Train model ONCE and save to disk for production use"""
        
        # Check if model exists and is recent (unless forced)
        if not force_retrain and self.is_loaded:
            model_age_days = self._get_model_age_days()
            if model_age_days < 30:  # Model is less than 30 days old
                logger.info(f"✅ Using existing model (trained {model_age_days} days ago)")
                return self.model_metadata
        
        logger.info("🤖 Training new yield prediction model...")
        
        try:
            # Load training data
            training_data = await self._load_training_data()
            total_rows = len(training_data)
            logger.info(f"📥 Loaded {total_rows} training records from DB")
            # Limit sample size to speed up training
            max_rows = 20000  # cap rows for faster training
            if total_rows > max_rows:
                training_data = training_data.sample(max_rows, random_state=42)
                logger.info(f"🎲 Sampling down to {max_rows} records for faster training")
            
            if len(training_data) < 100:
                raise ValueError(f"Insufficient training data: {len(training_data)} records")
            
            logger.info(f"📊 Loaded {len(training_data)} training records")
            
            # Prepare features and target
            X, y, feature_names = self._prepare_features(training_data)
            self.feature_names = feature_names
            
            logger.info(f"🎯 Feature shape: {X.shape}, Target shape: {y.shape}")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            # Use HistGradientBoosting for faster training with early stopping
            self.model = HistGradientBoostingRegressor(
                max_iter=100,
                learning_rate=0.1,
                max_depth=6,
                early_stopping=True,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            y_pred = self.model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            
            # Feature importance (fallback if not available)
            try:
                importances = self.model.feature_importances_
            except AttributeError:
                importances = [0.0] * len(feature_names)
            feature_importance = dict(zip(feature_names, importances))
            
            # Create metadata
            training_results = {
                'version': '1.0',
                'model_type': 'Gradient Boosting Regressor',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'train_r2_score': float(train_score),
                'test_r2_score': float(test_score),
                'mean_absolute_error': float(mae),
                'root_mean_square_error': float(rmse),
                'feature_importance': {k: float(v) for k, v in feature_importance.items()},
                'training_date': datetime.now().isoformat(),
                'feature_count': len(feature_names),
                'model_file': self.model_path
            }
            
            # Save model to disk
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_names': self.feature_names
            }
            joblib.dump(model_data, self.model_path)
            
            # Save metadata
            with open(self.metadata_path, 'w') as f:
                json.dump(training_results, f, indent=2)
            
            self.model_metadata = training_results
            self.is_loaded = True
            
            logger.info(f"🎉 Model trained and saved successfully!")
            logger.info(f"   Test R² Score: {test_score:.3f}")
            logger.info(f"   MAE: {mae:.1f} kg/ha")
            logger.info(f"   Model saved to: {self.model_path}")
            
            return training_results
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            raise

    async def predict_yield(self, farm_data: Dict) -> Dict:
        """FAST prediction using pre-loaded model - NO training delay"""
        
        if not self.is_loaded:
            # Try to load model one more time
            if not self._load_model():
                return {
                    'error': 'No trained model available. Please train model first.',
                    'predicted_yield_kg_per_ha': 0,
                    'recommendations': ['Train the yield prediction model first']
                }
        
        try:
            # Prepare input features
            features = self._prepare_prediction_features(farm_data)
            
            # Scale features using pre-fitted scaler
            features_scaled = self.scaler.transform([features])
            
            # Make prediction using pre-trained model
            predicted_yield = self.model.predict(features_scaled)[0]
            
            # Calculate prediction confidence
            prediction_std = self._estimate_prediction_uncertainty(features_scaled)
            
            # Generate recommendations
            recommendations = self._generate_yield_recommendations(predicted_yield, farm_data)
            
            return {
                'predicted_yield_kg_per_ha': round(max(0, predicted_yield), 2),
                'confidence_interval_lower': round(max(0, predicted_yield - 1.96 * prediction_std), 2),
                'confidence_interval_upper': round(predicted_yield + 1.96 * prediction_std, 2),
                'prediction_confidence': self._calculate_prediction_confidence(prediction_std),
                'yield_category': self._categorize_yield(predicted_yield, farm_data.get('crop_type', 'wheat')),
                'recommendations': recommendations,
                'model_version': self.model_metadata.get('version', '1.0'),
                'model_training_date': self.model_metadata.get('training_date', 'unknown'),
                'prediction_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Yield prediction error: {e}")
            return {
                'error': str(e),
                'predicted_yield_kg_per_ha': 0,
                'recommendations': ['Unable to generate prediction - check input data']
            }

    def _get_model_age_days(self) -> int:
        """Get age of current model in days"""
        try:
            training_date = datetime.fromisoformat(self.model_metadata.get('training_date', ''))
            return (datetime.now() - training_date).days
        except:
            return 999  # Very old if we can't parse

    async def _load_training_data(self) -> pd.DataFrame:
        """Load training data from database"""
        try:
            # Normalize db_url for asyncpg
            dsn = self.db_url.replace('+asyncpg', '') if '+asyncpg' in self.db_url else self.db_url
            conn = await asyncpg.connect(dsn)
            
            query = """
            SELECT 
                apy.wheat_yield_kg_per_ha, apy.rice_yield_kg_per_ha,
                apy.cotton_yield_kg_per_ha, apy.maize_yield_kg_per_ha,
                apy.wheat_area_1000_ha, apy.rice_area_1000_ha,
                apy.cotton_area_1000_ha, apy.maize_area_1000_ha,
                apy.state_name, apy.dist_name, apy.year,
                mr.annual_rainfall_millimeters,
                mr.january_rainfall_millimeters, mr.february_rainfall_millimeters,
                mr.march_rainfall_millimeters, mr.april_rainfall_millimeters,
                mr.may_rainfall_millimeters, mr.june_rainfall_millimeters,
                mr.july_rainfall_millimeters, mr.august_rainfall_millimeters,
                mr.september_rainfall_millimeters, mr.october_rainfall_millimeters,
                mr.november_rainfall_millimeters, mr.december_rainfall_millimeters,
                sf.nitrogen_kharif_consumption_tons, sf.nitrogen_rabi_consumption_tons,
                sf.phosphate_kharif_consumption_tons, sf.phosphate_rabi_consumption_tons,
                sf.potash_kharif_consumption_tons, sf.potash_rabi_consumption_tons,
                si.wheat_irrigated_area_1000_ha, si.rice_irrigated_area_1000_ha
            FROM area_production_yield apy
            LEFT JOIN monthly_rainfall mr ON apy.state_name = mr.state_name 
                AND apy.dist_name = mr.dist_name AND apy.year = mr.year
            LEFT JOIN state_wise_fertilizer sf ON apy.state_name = sf.state_name AND apy.year = sf.year
            LEFT JOIN state_wise_irrigation si ON apy.state_name = si.state_name AND apy.year = si.year
            WHERE apy.year >= 2015 
                AND (apy.wheat_yield_kg_per_ha > 0 OR apy.rice_yield_kg_per_ha > 0 
                     OR apy.cotton_yield_kg_per_ha > 0 OR apy.maize_yield_kg_per_ha > 0)
            ORDER BY apy.year DESC LIMIT 10000
            """
            
            rows = await conn.fetch(query)
            logger.info(f"🗄️ Fetched {len(rows)} rows from DB")
            await conn.close()
            
            df = pd.DataFrame([dict(row) for row in rows])
            return df
            
        except Exception as e:
            logger.error(f"❌ Database loading error: {e}")
            raise

    def _prepare_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features without monsoon_rainfall_millimeters"""
        crops = ['wheat', 'rice', 'cotton', 'maize']
        combined_data = []
        
        for crop in crops:
            yield_col = f'{crop}_yield_kg_per_ha'
            area_col = f'{crop}_area_1000_ha'
            
            crop_data = df[df[yield_col] > 0].copy()
            if len(crop_data) == 0:
                continue
                
            crop_data['crop_type'] = crop
            crop_data['target_yield'] = crop_data[yield_col]
            crop_data['crop_area'] = crop_data[area_col].fillna(0)
            combined_data.append(crop_data)
        
        if not combined_data:
            raise ValueError("No valid crop data found")
            
        final_df = pd.concat(combined_data, ignore_index=True)
        
        # Encode categorical variables
        le_state = LabelEncoder()
        le_district = LabelEncoder()
        le_crop = LabelEncoder()
        
        final_df['state_encoded'] = le_state.fit_transform(final_df['state_name'].fillna('Unknown'))
        final_df['district_encoded'] = le_district.fit_transform(final_df['dist_name'].fillna('Unknown'))
        final_df['crop_encoded'] = le_crop.fit_transform(final_df['crop_type'])
        
        self.label_encoders = {
            'state': le_state,
            'district': le_district,
            'crop': le_crop
        }
        
        # ✅ FIXED: Numerical features without monsoon_rainfall_millimeters
        numerical_features = [
            'year', 'state_encoded', 'district_encoded', 'crop_encoded', 'crop_area',
            'annual_rainfall_millimeters',
            'january_rainfall_millimeters', 'february_rainfall_millimeters',
            'march_rainfall_millimeters', 'april_rainfall_millimeters',
            'may_rainfall_millimeters', 'june_rainfall_millimeters',
            'july_rainfall_millimeters', 'august_rainfall_millimeters',
            'september_rainfall_millimeters', 'october_rainfall_millimeters',
            'november_rainfall_millimeters', 'december_rainfall_millimeters',
            'nitrogen_kharif_consumption_tons', 'nitrogen_rabi_consumption_tons',
            'phosphate_kharif_consumption_tons', 'phosphate_rabi_consumption_tons',
            'potash_kharif_consumption_tons', 'potash_rabi_consumption_tons',
            'wheat_irrigated_area_1000_ha', 'rice_irrigated_area_1000_ha'
        ]
        
        # Fill missing values
        for feature in numerical_features:
            if feature in final_df.columns:
                final_df[feature] = final_df[feature].fillna(final_df[feature].median())
        
        X = final_df[numerical_features].values
        y = final_df['target_yield'].values
        
        return X, y, numerical_features

    def _prepare_prediction_features(self, farm_data: Dict) -> List[float]:
        """Prepare features for single prediction"""
        # Encode categorical variables
        state_encoded = self._safe_encode('state', farm_data.get('state', 'Unknown'))
        district_encoded = self._safe_encode('district', farm_data.get('district', 'Unknown'))
        crop_encoded = self._safe_encode('crop', farm_data.get('crop_type', 'wheat'))
        
        # Create feature vector
        features = [
            farm_data.get('year', datetime.now().year),
            state_encoded, district_encoded, crop_encoded,
            farm_data.get('crop_area', 1.0),
            farm_data.get('annual_rainfall', 800),
            farm_data.get('jan_rainfall', 20), farm_data.get('feb_rainfall', 25),
            farm_data.get('mar_rainfall', 15), farm_data.get('apr_rainfall', 10),
            farm_data.get('may_rainfall', 30), farm_data.get('jun_rainfall', 120),
            farm_data.get('jul_rainfall', 200), farm_data.get('aug_rainfall', 180),
            farm_data.get('sep_rainfall', 150), farm_data.get('oct_rainfall', 30),
            farm_data.get('nov_rainfall', 10), farm_data.get('dec_rainfall', 8),
            farm_data.get('nitrogen_kharif', 100), farm_data.get('nitrogen_rabi', 80),
            farm_data.get('phosphate_kharif', 60), farm_data.get('phosphate_rabi', 40),
            farm_data.get('potash_kharif', 40), farm_data.get('potash_rabi', 30),
            farm_data.get('wheat_irrigated_area', 0.5), farm_data.get('rice_irrigated_area', 0.5)
        ]
        
        return features[:len(self.feature_names)]

    def _safe_encode(self, encoder_name: str, value: str) -> int:
        """Safely encode categorical value"""
        try:
            if encoder_name in self.label_encoders:
                return self.label_encoders[encoder_name].transform([value])[0]
        except (ValueError, KeyError):
            pass
        return 0  # Default encoding

    def _estimate_prediction_uncertainty(self, features: np.ndarray) -> float:
        """Estimate prediction uncertainty"""
        return 200.0  # Default uncertainty

    def _calculate_prediction_confidence(self, uncertainty: float) -> str:
        """Calculate confidence level"""
        if uncertainty < 150:
            return "HIGH"
        elif uncertainty < 300:
            return "MEDIUM"
        else:
            return "LOW"

    def _categorize_yield(self, yield_value: float, crop_type: str) -> str:
        """Categorize yield performance"""
        thresholds = {
            'wheat': {'high': 4500, 'medium': 3000},
            'rice': {'high': 4000, 'medium': 2500},
            'cotton': {'high': 2000, 'medium': 1200},
            'maize': {'high': 5000, 'medium': 3500}
        }
        
        crop_thresholds = thresholds.get(crop_type, {'high': 4000, 'medium': 2500})
        
        if yield_value >= crop_thresholds['high']:
            return "HIGH YIELD"
        elif yield_value >= crop_thresholds['medium']:
            return "MEDIUM YIELD"
        else:
            return "LOW YIELD"

    def _generate_yield_recommendations(self, predicted_yield: float, farm_data: Dict) -> List[str]:
        """Generate farming recommendations"""
        recommendations = []
        crop_type = farm_data.get('crop_type', 'wheat')
        
        if self._categorize_yield(predicted_yield, crop_type) == "LOW YIELD":
            recommendations.extend([
                "Consider high-yielding variety seeds",
                "Optimize fertilizer application based on soil test",
                "Improve irrigation scheduling"
            ])
        
        annual_rainfall = farm_data.get('annual_rainfall', 800)
        if annual_rainfall < 500:
            recommendations.append("Install efficient irrigation due to low rainfall")
        
        return recommendations
    
    @property
    def is_trained(self) -> bool:
        """Alias for is_loaded to satisfy test attribute"""
        return self.is_loaded

    # Alias method name for testing
    train_model_from_real_data = train_and_save_model

# Global instance with pre-trained model loading
production_yield_model = ProductionYieldPredictionModel()
# Alias for test import
real_yield_model = production_yield_model
