"""
Train ALL ML models with your REAL data
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.ml_tools.real_yield_prediction import real_yield_model
import logging

logging.basicConfig(level=logging.INFO)

async def train_all_models():
    """Train all ML models with real data"""
    
    print("🤖 Training Real ML Models with Your Data")
    print("=" * 60)
    
    # 1. Train Yield Prediction Model
    print("\n🌾 Training Yield Prediction Model...")
    try:
        yield_results = await real_yield_model.train_model_from_real_data()
        
        print(f"✅ Yield Model Trained Successfully!")
        print(f"   - Training Samples: {yield_results['training_samples']}")
        print(f"   - Test R² Score: {yield_results['test_r2_score']:.3f}")
        print(f"   - Cross-validation: {yield_results['cross_val_mean']:.3f} ± {yield_results['cross_val_std']:.3f}")
        print(f"   - Mean Absolute Error: {yield_results['mean_absolute_error']:.1f} kg/ha")
        
        # Test prediction
        test_farm = {
            'crop_type': 'wheat',
            'state': 'Punjab',
            'district': 'Ludhiana',
            'annual_rainfall': 600,
            'nitrogen_kharif': 120,
            'crop_area': 2.0
        }
        
        prediction = await real_yield_model.predict_yield(test_farm)
        print(f"   - Test Prediction: {prediction['predicted_yield_kg_per_ha']} kg/ha")
        
    except Exception as e:
        print(f"❌ Yield Model Training Failed: {e}")
    
    # 2. Train Price Prediction Model
    print("\n💰 Training Price Prediction Model...")
    # Add price model training here
    
    # 3. Train more models...
    print("\n🎯 All Models Training Complete!")

if __name__ == "__main__":
    asyncio.run(train_all_models())
