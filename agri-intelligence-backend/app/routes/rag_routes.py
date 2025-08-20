"""
FastAPI endpoint for agricultural intelligence

File: app/routes/rag_routes.py
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import time
from datetime import datetime

# Import the correct RAG function
from ..tools.rag_core.rag_orchestrator import process_agricultural_query

# Set up detailed logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["agricultural-intelligence"])

class FarmerQuery(BaseModel):
    query: str
    farmer_context: Optional[Dict[str, Any]] = None
    language: Optional[str] = "en"
    location: Optional[Dict[str, str]] = None

class QueryResponse(BaseModel):
    success: bool
    response: Dict[str, Any]
    processing_time: float
    confidence_score: float
    tools_used: list
    classification: Dict[str, Any]

@router.post("/ask", response_model=QueryResponse)
async def ask_agricultural_advisor(
    farmer_query: FarmerQuery,
    background_tasks: BackgroundTasks
) -> QueryResponse:
    """
    Main endpoint for agricultural intelligence queries
    
    Processes farmer questions and returns comprehensive agricultural advice
    using the complete RAG system with concurrent tool execution.
    """
    start_time = time.time()
    
    try:
        logger.info(f"🌾 Received agricultural query: {farmer_query.query[:100]}...")
        logger.info(f"📍 Location context: {farmer_query.location}")
        logger.info(f"🌐 Language: {farmer_query.language}")
        
        # Add location to farmer context if provided
        context = farmer_query.farmer_context or {}
        if farmer_query.location:
            context.update(farmer_query.location)
            logger.info(f"📍 Updated context with location: {context}")
        
        # Process query through RAG system with detailed logging
        logger.info("🔄 Starting RAG processing...")
        result = await process_agricultural_query(
            farmer_query.query,
            farmer_context=farmer_query.farmer_context
        )
        
        processing_time = time.time() - start_time
        logger.info(f"⏱️ Query processed in {processing_time:.2f} seconds")
        classification = result.get('classification')
        if classification:
            primary_cat = getattr(classification, 'primary_category', None) or classification.get('primary_category', 'unknown') if isinstance(classification, dict) else 'unknown'
            confidence = getattr(classification, 'confidence', None) or classification.get('confidence', 0.0) if isinstance(classification, dict) else 0.0
        else:
            primary_cat, confidence = 'unknown', 0.0
        logger.info(f"🎯 Classification: {primary_cat}")
        logger.info(f"💯 Confidence: {confidence:.2f}")

        if result and 'response' in result:
            background_tasks.add_task(
                log_query_analytics,
                farmer_query.query,
                primary_cat,
                processing_time
            )
            normalized_response = result['response'] if isinstance(result['response'], dict) else {'main_answer': result['response']}
            return QueryResponse(
                success=True,
                response=normalized_response,
                processing_time=processing_time,
                confidence_score=confidence,
                tools_used=result.get('tools_used', []),
                classification={'primary_category': primary_cat, 'confidence': confidence}
            )
        logger.error(f"❌ RAG processing failed: {result}")
        raise HTTPException(
            status_code=500,
            detail="Query processing failed: No valid response generated"
        )
            
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"❌ API endpoint error after {processing_time:.2f}s: {e}")
        logger.error(f"📝 Query was: {farmer_query.query}")
        import traceback
        logger.error(f"🔍 Full traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Agricultural intelligence system error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test RAG system health
        test_result = await process_agricultural_query("Test query for health check")
        rag_healthy = test_result is not None
        
        # Check model health
        try:
            from ..tools.model_startup import check_model_health
            model_status = check_model_health()
            logger.info(f"🏥 Model health: {model_status}")
        except Exception as e:
            model_status = {"error": str(e)}
            logger.error(f"❌ Model health check failed: {e}")
        
        return {
            "status": "healthy" if rag_healthy else "degraded",
            "service": "Agricultural Intelligence RAG System",
            "rag_system": "operational" if rag_healthy else "error",
            "models": model_status,
            "version": "1.0",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "error", 
            "service": "Agricultural Intelligence RAG System",
            "error": str(e),
            "version": "1.0",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/categories")
async def get_query_categories():
    """Get available query categories"""
    return {
        "categories": [
            "weather_impact",
            "irrigation_planning", 
            "market_price_forecasting",
            "crop_selection",
            "yield_prediction",
            "pest_disease_management",
            "fertilizer_optimization",
            "government_schemes",
            "financial_planning",
            "seasonal_planning",
            "soil_health"
        ],
        "description": "Agricultural intelligence query categories"
    }

async def log_query_analytics(query: str, classification: str, processing_time: float):
    """Background task for logging analytics"""
    logger.info(f"📊 Analytics: {classification} query processed in {processing_time:.2f}s")
    logger.info(f"📝 Query content: {query[:100]}...")
    # Additional analytics logic can be added here
