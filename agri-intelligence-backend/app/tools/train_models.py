"""
Pre-train all ML models for production deployment
Run this ONCE to train and save models
"""
import asyncio
import sys
import os
from pathlib import Path
 # Manually load .env variables before any model imports
env_file = Path(__file__).parent.parent.parent / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        if not line or line.strip().startswith('#'):
            continue
        key, sep, val = line.partition('=')
        if sep and key and val:
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))

from ml_tools.real_yield_prediction import production_yield_model
import logging

logging.basicConfig(level=logging.INFO)

async def train_all_models():
    """Train all ML models and save to disk"""
    print("🤖 TRAINING PRODUCTION ML MODELS")
    print("=" * 60)
    print("This will train models ONCE and save them for fast loading")
    print()
    
    # Train yield prediction model
    print("🌾 Training Yield Prediction Model...")
    try:
        results = await production_yield_model.train_and_save_model(force_retrain=True)
        
        print("✅ Yield Prediction Model Trained Successfully!")
        print(f"   R² Score: {results['test_r2_score']:.3f}")
        print(f"   MAE: {results['mean_absolute_error']:.1f} kg/ha")
        print(f"   Training Records: {results['training_samples']}")
        print(f"   Model File: {results['model_file']}")
        print()
        
        # Test prediction
        test_data = {
            'crop_type': 'wheat',
            'state': 'Punjab',
            'district': 'Ludhiana',
            'annual_rainfall': 600,
            'nitrogen_kharif': 120
        }
        
        prediction = await production_yield_model.predict_yield(test_data)
        print(f"🧪 Test Prediction: {prediction['predicted_yield_kg_per_ha']} kg/ha")
        print(f"   Confidence: {prediction['prediction_confidence']}")
        
    except Exception as e:
        print(f"❌ Yield Model Training Failed: {e}")
    
    print("\n🎉 MODEL TRAINING COMPLETE!")
    print("Models are now saved and ready for production use.")
    print("Restart your application to use pre-trained models.")

if __name__ == "__main__":
    asyncio.run(train_all_models())
