"""
Model startup and initialization for production deployment
Checks if models exist, trains them if needed
"""
import asyncio
import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

async def initialize_models():
    """Initialize ML models on startup - train if needed"""
    try:
        # Check if models already exist
        models_dir = Path(__file__).parent.parent.parent / 'models'
        yield_model_file = models_dir / 'production_yield_model.joblib'
        
        if yield_model_file.exists():
            logger.info("🤖 Pre-trained models found - loading existing models")
            
            # Test if models work
            try:
                # Add the tools directory to the path for relative imports
                tools_dir = Path(__file__).parent
                if str(tools_dir) not in sys.path:
                    sys.path.insert(0, str(tools_dir))
                
                from ml_tools.real_yield_prediction import production_yield_model
                
                # Quick test prediction to ensure model works
                test_data = {
                    'crop_type': 'wheat',
                    'state': 'Punjab', 
                    'district': 'Ludhiana',
                    'annual_rainfall': 600,
                    'nitrogen_kharif': 120
                }
                
                prediction = await production_yield_model.predict_yield(test_data)
                logger.info(f"✅ Models loaded successfully - test prediction: {prediction['predicted_yield_kg_per_ha']} kg/ha")
                return True
                
            except Exception as e:
                logger.warning(f"⚠️  Existing models failed to load: {e}")
                logger.info("🔄 Will retrain models...")
        
        # Models don't exist or failed to load - train them
        logger.info("🤖 Training ML models on first startup...")
        
        # Add tools directory to path for relative imports
        tools_dir = Path(__file__).parent
        if str(tools_dir) not in sys.path:
            sys.path.insert(0, str(tools_dir))
        
        from train_models import train_all_models
        await train_all_models()
        return True
        
    except Exception as e:
        logger.error(f"❌ Model initialization failed: {e}")
        logger.info("🔄 Continuing with fallback models...")
        return False

def check_model_health():
    """Check health of all ML models."""
    from .ml_tools.real_yield_prediction import is_model_trained
    
    health = {}
    try:
        health["yield_model"] = is_model_trained
    except Exception as e:
        health["yield_model"] = f"error: {str(e)}"
    
    return health
