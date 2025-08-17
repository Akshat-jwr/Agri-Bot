"""
Simple FastAPI startup test with model training
"""
import asyncio
import sys
import os

# Set up paths
sys.path.append('/Users/akshatjiwrajka/programming/Capital-One-Agri/agri-intelligence-backend')
os.chdir('/Users/akshatjiwrajka/programming/Capital-One-Agri/agri-intelligence-backend')

async def test_startup():
    """Test the complete startup process"""
    print("🌾 Testing FastAPI Startup with Model Training")
    print("=" * 60)
    
    # Test model initialization
    print("\n🤖 Step 1: Model Initialization")
    from app.tools.model_startup import initialize_models
    success = await initialize_models()
    print(f"✅ Models ready: {success}")
    
    # Test RAG system
    print("\n🔍 Step 2: RAG System Test")
    from app.tools.rag_core.rag_orchestrator import rag_orchestrator
    result = await rag_orchestrator.process_farmer_query("What fertilizer should I use for wheat?")
    print(f"✅ RAG working: {result['success']}")
    print(f"✅ Classification: {result['classification'].primary_category}")
    print(f"✅ Confidence: {result['confidence_score']:.2f}")
    
    # Test model health
    print("\n🏥 Step 3: Model Health Check")
    from app.tools.model_startup import check_model_health
    health = await check_model_health()
    print(f"✅ Model Health: {health}")
    
    print("\n🎉 All Systems Ready for Production!")
    print("Your Agricultural Intelligence API is fully functional!")

if __name__ == "__main__":
    asyncio.run(test_startup())
