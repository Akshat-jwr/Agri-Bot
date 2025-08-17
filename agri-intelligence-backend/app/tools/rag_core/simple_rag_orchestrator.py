"""
Simplified RAG Orchestrator for Agricultural Intelligence

This module provides a simplified but fully functional RAG system that works
with the current infrastructure, including Google Search and multilingual support.

File: app/tools/rag_core/simple_rag_orchestrator.py
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.tools.llm_tools.gemini_llm import agricultural_llm
from app.tools.rag_core.google_search_tool import google_search_tool
from app.language_processing.translator import agricultural_translator

logger = logging.getLogger(__name__)

class SimpleAgriculturalRAGOrchestrator:
    """
    Simplified agricultural intelligence RAG system with multilingual support
    """
    
    def __init__(self):
        self.performance_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'average_processing_time': 0
        }

    async def process_agricultural_query(self, 
                                       farmer_query: str, 
                                       farmer_location: Optional[str] = None,
                                       user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete agricultural query processing with Google Search and multilingual support
        
        Pipeline:
        1. Language Detection & Translation to English
        2. Google Search for latest information
        3. Context fusion with expert LLM generation
        4. Response translation back to original language
        """
        start_time = datetime.now()
        self.performance_metrics['total_queries'] += 1
        
        try:
            logger.info(f"🌾 Processing agricultural query: {farmer_query[:100]}...")
            
            # Step 1: Language Processing - Detect and translate to English
            logger.info("🌐 Step 1: Processing language and translation...")
            english_query, original_language = agricultural_translator.query_to_english(farmer_query)
            logger.info(f"Language: {original_language} → English: {english_query}")
            
            # Step 2: Google Search for latest information
            logger.info("🔍 Step 2: Searching for latest agricultural information...")
            search_results = await google_search_tool.search_agricultural_info(
                query=english_query,
                location=farmer_location,
                num_results=3
            )
            
            # Step 3: Context preparation and LLM generation
            logger.info("🧠 Step 3: Generating expert agricultural response...")
            
            # Create a simple classification based on keywords
            classification = self._simple_classify_query(english_query)
            
            context_data = {
                'search_results': search_results,
                'weather_intelligence': {},
                'market_intelligence': {},
                'agricultural_data': {},
                'government_info': {},
                'web_intelligence': search_results
            }
            
            # Generate expert response using Gemini LLM
            expert_response = await agricultural_llm.generate_agricultural_response(
                query=english_query,
                classification=classification,
                context_data=context_data,
                farmer_context={'location': farmer_location}
            )
            
            # Step 4: Translate response back to original language
            final_response = expert_response
            if original_language != 'en':
                logger.info(f"🌐 Step 4: Translating response back to {original_language}...")
                final_response = agricultural_translator.response_to_original_language(
                    expert_response, original_language
                )
            
            # Performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.performance_metrics['successful_queries'] += 1
            
            result = {
                'success': True,
                'response': final_response,
                'english_response': expert_response,  # Keep English version for logging
                'metadata': {
                    'original_language': original_language,
                    'english_query': english_query,
                    'processing_time_seconds': processing_time,
                    'search_results_count': len(search_results),
                    'search_results_preview': [
                        {
                            'title': r.get('title', 'No title')[:100],
                            'source': r.get('source', 'Unknown'),
                            'relevance': r.get('relevance_score', 0.5)
                        } for r in search_results[:3]
                    ] if search_results else [],
                    'location': farmer_location,
                    'query_category': classification.get('primary_category', 'general_farming'),
                    'timestamp': start_time.isoformat(),
                    'expert_consulted': agricultural_llm.get_expert_specialization(
                        classification.get('primary_category', 'general_farming')
                    ),
                    'context_sources': {
                        'google_search_results': len(search_results),
                        'weather_data': len(context_data.get('weather_intelligence', {})),
                        'market_data': len(context_data.get('market_intelligence', {})),
                        'agricultural_knowledge': len(context_data.get('agricultural_data', {}))
                    }
                }
            }
            
            logger.info(f"✅ Query processed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error processing agricultural query: {e}")
            
            # Fallback response in original language
            processing_time = (datetime.now() - start_time).total_seconds()
            original_language = original_language if 'original_language' in locals() else 'unknown'
            
            fallback_response = f"I apologize, but I encountered an error processing your query. Please try again or contact our support team."
            if original_language != 'en' and original_language != 'unknown':
                fallback_response = agricultural_translator.response_to_original_language(
                    fallback_response, original_language
                )
            
            return {
                'success': False,
                'response': fallback_response,
                'error': str(e),
                'metadata': {
                    'original_language': original_language,
                    'processing_time_seconds': processing_time,
                    'timestamp': start_time.isoformat()
                }
            }

    def _simple_classify_query(self, query: str) -> Dict[str, Any]:
        """
        Simple keyword-based query classification
        """
        query_lower = query.lower()
        
        # Category keywords mapping
        categories = {
            'fertilizer_optimization': ['fertilizer', 'fertiliser', 'npk', 'urea', 'nutrients', 'nutrition'],
            'weather_impact': ['weather', 'rain', 'drought', 'monsoon', 'climate', 'temperature'],
            'crop_selection': ['crop', 'variety', 'seed', 'cultivation', 'growing', 'plant'],
            'pest_disease_management': ['pest', 'disease', 'insects', 'fungus', 'pesticide', 'spray'],
            'yield_prediction': ['yield', 'production', 'harvest', 'productivity', 'output'],
            'market_price_forecasting': ['price', 'market', 'sell', 'rate', 'cost', 'profit'],
            'soil_health': ['soil', 'ph', 'organic', 'compost', 'erosion'],
            'irrigation_planning': ['irrigation', 'water', 'drip', 'sprinkler', 'watering'],
            'government_schemes': ['scheme', 'subsidy', 'government', 'loan', 'support'],
            'seasonal_planning': ['season', 'planning', 'calendar', 'timing', 'schedule']
        }
        
        # Find best matching category
        best_category = 'general_farming'
        max_matches = 0
        
        for category, keywords in categories.items():
            matches = sum(1 for keyword in keywords if keyword in query_lower)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return {
            'primary_category': best_category,
            'confidence': min(0.8, 0.3 + (max_matches * 0.1)),
            'extracted_entities': {
                'crops': self._extract_crops(query_lower),
                'locations': self._extract_locations(query_lower)
            },
            'urgency': 'medium'
        }
    
    def _extract_crops(self, query: str) -> List[str]:
        """Extract crop names from query"""
        crops = ['wheat', 'rice', 'cotton', 'sugarcane', 'maize', 'barley', 'soybean', 'potato', 'tomato']
        return [crop for crop in crops if crop in query]
    
    def _extract_locations(self, query: str) -> List[str]:
        """Extract location names from query"""
        locations = ['punjab', 'haryana', 'uttar pradesh', 'bihar', 'maharashtra', 'gujarat', 'rajasthan']
        return [location for location in locations if location in query]

# Global instance
simple_rag_orchestrator = SimpleAgriculturalRAGOrchestrator()

# For backward compatibility
async def process_agricultural_query(farmer_query: str, 
                                   farmer_location: Optional[str] = None,
                                   user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Backward compatible function for processing agricultural queries
    """
    return await simple_rag_orchestrator.process_agricultural_query(
        farmer_query, farmer_location, user_id
    )
