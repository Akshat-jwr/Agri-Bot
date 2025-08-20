"""
RAG Orchestrator - Coordinates all RAG components for agricultural intelligence

This module orchestrates the complete Retrieval-Augmented Generation pipeline for agricultural queries.
It coordinates the vector database, weather API, yield prediction models, Google Search, language processing,
and LLM integration to provide comprehensive agricultural intelligence responses.

File: app/tools/rag_core/rag_orchestrator.py
"""

import asyncio
import logging
import traceback
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

try:
    from app.tools.vector_db.chroma_manager import chroma_manager
except ImportError:
    chroma_manager = None
    
try:
    from app.tools.api_tools.real_weather_apis import weather_api
except ImportError:
    weather_api = None
    
try:
    from app.tools.models.yield_predictor import yield_predictor
except ImportError:
    yield_predictor = None
    
from app.tools.llm_tools.gemini_llm import agricultural_llm
from app.tools.rag_core.google_search_tool import google_search_tool
from app.language_processing.translator import agricultural_translator

logger = logging.getLogger(__name__)

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .query_classifier import query_classifier, QueryClassification
from .tool_orchestrator import tool_orchestrator
from .context_fusion import context_fusion, FusedContext
from .google_search_tool import google_search_tool

logger = logging.getLogger(__name__)

class AgriculturalRAGOrchestrator:
    """
    Main orchestrator for agricultural intelligence RAG system
    Coordinates query understanding, tool execution, and response generation
    """
    
    def __init__(self):
        self.max_processing_time = 10.0  # Maximum processing time in seconds
        self.performance_metrics = {
            'total_queries': 0,
            'successful_queries': 0,
            'average_processing_time': 0,
            'tool_usage_stats': {}
        }

    async def process_farmer_query(self, 
                                 query: str,
                                 farmer_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        ENHANCED: Main entry point for multilingual farmer queries with Google Search
        Returns comprehensive agricultural intelligence response with language support
        """
        start_time = datetime.now()
        self.performance_metrics['total_queries'] += 1
        
        logger.info(f"🌾 Processing farmer query: '{query[:50]}...'")
        
        try:
            # Step 1: Language Detection & Translation
            logger.info("🌐 Step 1: Processing language and translation...")
            english_query, original_language = agricultural_translator.query_to_english(query)
            logger.info(f"Language: {original_language} → English: {english_query}")
            
            # Step 2: Classify the English query
            logger.info("🔍 Step 2: Classifying query...")
            classification = await query_classifier.classify_query(english_query, farmer_context)
            
            logger.info(f"✅ Classification: {classification.primary_category} "
                       f"(confidence: {classification.confidence:.2f})")
            
            # Step 3: Google Search for latest information
            logger.info("🔍 Step 3: Searching for latest agricultural information...")
            search_results = await google_search_tool.search_agricultural_info(
                query=english_query,
                location=farmer_context.get('location') if farmer_context else None,
                num_results=3
            )
            
            # Step 4: Execute tools concurrently
            logger.info("🔧 Step 4: Executing tools concurrently...")
            tool_results = await tool_orchestrator.orchestrate_tools(classification, farmer_context)
            
            # Add search results to tool results
            tool_results['google_search'] = type('SearchResult', (), {
                'success': True,
                'data': search_results,
                'confidence': 0.8,
                'processing_time': 0.5,
                'metadata': {'source': 'google_custom_search'}
            })()
            
            successful_tools = [name for name, result in tool_results.items() if result.success]
            logger.info(f"✅ Tool execution complete: {len(successful_tools)}/{len(tool_results)} successful")
            
            # Step 5: Fuse context from all tools
            logger.info("🔗 Step 5: Fusing context from all sources...")
            fused_context = await context_fusion.fuse_tool_results(tool_results, classification)
            logger.info(f"Fused context raw type: {type(fused_context)}")
            # Defensive: some legacy paths may return a dict instead of FusedContext
            if isinstance(fused_context, dict):  # normalize
                from types import SimpleNamespace
                fused_context = SimpleNamespace(**fused_context)  # minimal attribute access support
                logger.warning("Normalized dict fused_context to SimpleNamespace")
            
            # Step 6: Generate comprehensive response with enhanced context
            logger.info("📝 Step 6: Generating expert agricultural response...")
            # Build enhanced context robustly (fallback to getattr with default empty dict)
            enhanced_context = {
                'weather_intelligence': getattr(fused_context, 'weather_intelligence', {}),
                'market_intelligence': getattr(fused_context, 'market_intelligence', {}),
                'agricultural_data': getattr(fused_context, 'agricultural_data', {}),
                'government_info': getattr(fused_context, 'government_info', {}),
                'web_intelligence': getattr(fused_context, 'web_intelligence', {}),
                'confidence_score': getattr(fused_context, 'confidence_score', 0.5),
                'data_freshness': getattr(fused_context, 'data_freshness', 'standard'),
                'synthesis_summary': getattr(fused_context, 'synthesis_summary', ''),
                'search_results': search_results,
                'original_query': query,
                'english_query': english_query,
                'original_language': original_language
            }
            
            response = await self._generate_multilingual_farmer_response(
                english_query, classification, enhanced_context, tool_results, original_language
            )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            self.performance_metrics['successful_queries'] += 1
            
            # Update performance metrics
            self._update_performance_metrics(processing_time, tool_results)
            
            logger.info(f"🎉 Query processed successfully in {processing_time:.2f} seconds")
            
            return {
                'success': True,
                'response': response,
                'english_response': response if original_language == 'en' else None,
                'classification': classification,
                'fused_context': fused_context,
                'processing_time': processing_time,
                'tools_used': list(tool_results.keys()),
                'confidence_score': getattr(fused_context, 'confidence_score', 0.5),
                'metadata': {
                    'original_language': original_language,
                    'english_query': english_query,
                    'search_results_count': len(search_results)
                }
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Query processing failed: {e}\n{traceback.format_exc()}")
            # Attempt to extract tool result names if available
            debug_tools = []
            try:
                if 'tool_results' in locals():
                    debug_tools = list(tool_results.keys())
            except Exception:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'processing_time': processing_time,
                'fallback_response': self._generate_fallback_response(query),
                'debug_tools': debug_tools
            }

    async def _generate_farmer_response(self, 
                                      query: str,
                                      classification: QueryClassification,
                                      fused_context: FusedContext,
                                      tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive farmer-friendly response using Gemini LLM
        """
        logger.info("🤖 Generating intelligent response with Gemini LLM...")
        
        # Call Gemini LLM for intelligent main answer
        main_answer = await agricultural_llm.generate_agricultural_response(
            query=query,
            classification=classification.__dict__,
            context_data={
                'weather_intelligence': fused_context.weather_intelligence,
                'market_intelligence': fused_context.market_intelligence,
                'agricultural_data': fused_context.agricultural_data,
                'government_info': fused_context.government_info,
                'web_intelligence': fused_context.web_intelligence
            }
        )
        
        logger.info(f"✅ Generated {len(main_answer)} character LLM response")
        
        response = {
            'main_answer': main_answer,  # NOW USING REAL LLM!
            'weather_guidance': self._extract_weather_guidance(fused_context.weather_intelligence),
            'market_advice': self._extract_market_advice(fused_context.market_intelligence),
            'agricultural_recommendations': self._extract_agri_recommendations(fused_context.agricultural_data),
            'government_benefits': self._extract_government_benefits(fused_context.government_info),
            'action_items': self._generate_action_items(classification, fused_context),
            'confidence_level': self._interpret_confidence(fused_context.confidence_score),
            'data_sources': self._list_data_sources(tool_results),
            'follow_up_questions': self._suggest_follow_ups(classification)
        }
        
        return response

    async def _generate_multilingual_farmer_response(self, 
                                                   english_query: str,
                                                   classification: QueryClassification,
                                                   enhanced_context: Dict,
                                                   tool_results: Dict[str, Any],
                                                   original_language: str) -> Dict[str, Any]:
        """
        Generate comprehensive multilingual farmer-friendly response using Gemini LLM
        """
        logger.info("🤖 Generating intelligent multilingual response with Gemini LLM...")
        
        # Create enhanced context for LLM
        context_data = {
            'weather_intelligence': enhanced_context.get('weather_intelligence'),
            'market_intelligence': enhanced_context.get('market_intelligence'), 
            'agricultural_data': enhanced_context.get('agricultural_data'),
            'government_info': enhanced_context.get('government_info'),
            'web_intelligence': enhanced_context.get('web_intelligence'),
            'search_results': enhanced_context.get('search_results', [])
        }
        
        # Call Gemini LLM for intelligent main answer in English
        english_main_answer = await agricultural_llm.generate_agricultural_response(
            query=english_query,
            classification=classification.__dict__,
            context_data=context_data
        )
        
        logger.info(f"✅ Generated {len(english_main_answer)} character LLM response")
        
        # Translate main answer to original language if needed
        main_answer = english_main_answer
        if original_language != 'en':
            logger.info(f"🌐 Translating main answer to {original_language}...")
            main_answer = agricultural_translator.response_to_original_language(
                english_main_answer, original_language
            )
        
        # Generate other response components (keeping English for now, can be enhanced later)
        response = {
            'main_answer': main_answer,  # Multilingual main response
            'english_main_answer': english_main_answer,  # Keep English version
            'weather_guidance': self._extract_weather_guidance(enhanced_context.get('weather_intelligence')),
            'market_advice': self._extract_market_advice(enhanced_context.get('market_intelligence')),
            'agricultural_recommendations': self._extract_agri_recommendations(enhanced_context.get('agricultural_data')),
            'government_benefits': self._extract_government_benefits(enhanced_context.get('government_info')),
            'latest_info': self._extract_search_insights(enhanced_context.get('search_results', [])),
            'action_items': self._generate_action_items(classification, enhanced_context),
            'confidence_level': self._interpret_confidence(enhanced_context.get('confidence_score', 0.5)),
            'data_sources': self._list_enhanced_data_sources(tool_results),
            'follow_up_questions': self._suggest_follow_ups(classification),
            'language_info': {
                'original_language': original_language,
                'response_language': original_language,
                'translation_applied': original_language != 'en'
            }
        }
        
        return response

    def _extract_search_insights(self, search_results: List[Dict]) -> List[Dict]:
        """Extract key insights from Google Search results"""
        insights = []
        for result in search_results[:3]:  # Top 3 results
            insights.append({
                'title': result.get('title', ''),
                'summary': result.get('snippet', '')[:200] + '...',
                'source': result.get('source', ''),
                'relevance': result.get('relevance_score', 0.5),
                'url': result.get('url', '')
            })
        return insights

    def _list_enhanced_data_sources(self, tool_results: Dict) -> List[str]:
        """List all data sources including Google Search"""
        sources = self._list_data_sources(tool_results)
        if 'google_search' in tool_results:
            sources.append('Google Custom Search - Latest Agricultural Information')
        return sources

    async def _generate_main_answer(self, 
                                  classification: QueryClassification,
                                  fused_context: FusedContext) -> str:
        """Generate the main answer based on query category"""
        
        category_responses = {
            'weather_impact': self._generate_weather_response(fused_context),
            'market_price_forecasting': self._generate_market_response(fused_context),
            'yield_prediction': self._generate_yield_response(fused_context),
            'crop_selection': self._generate_crop_selection_response(fused_context),
            'government_schemes': self._generate_scheme_response(fused_context),
            'irrigation_planning': self._generate_irrigation_response(fused_context),
            'fertilizer_optimization': self._generate_fertilizer_response(fused_context),
            'pest_disease_management': self._generate_pest_response(fused_context),
            'soil_health': self._generate_soil_response(fused_context)
        }
        
        return category_responses.get(
            classification.primary_category,
            f"Based on your {classification.primary_category.replace('_', ' ')} query, here's comprehensive agricultural guidance from our data sources."
        )

    # Response generators for different categories
    def _generate_weather_response(self, context: FusedContext) -> str:
        weather = context.weather_intelligence
        current = weather.get('current_conditions', {})
        
        if current:
            temp = current.get('temperature', 'N/A')
            humidity = current.get('humidity', 'N/A')
            response = f"Current weather conditions: {temp}°C temperature, {humidity}% humidity. "
            
            advisories = weather.get('agricultural_advisories', [])
            if advisories:
                response += f"Agricultural advice: {advisories[0]}"
            
            return response
        
        return "Weather data is being analyzed to provide farming guidance."

    def _generate_market_response(self, context: FusedContext) -> str:
        market = context.market_intelligence
        prices = market.get('current_prices', [])
        
        if prices and len(prices) > 0:
            price_info = prices[0]
            commodity = price_info.get('commodity', 'crop')
            modal_price = price_info.get('modal_price', 'N/A')
            
            response = f"Current {commodity} market price: ₹{modal_price} per quintal. "
            
            recommendations = market.get('trading_recommendations', [])
            if recommendations:
                response += f"Trading advice: {recommendations[0]}"
            
            return response
        
        return "Market prices are being analyzed to provide trading guidance."

    def _generate_yield_response(self, context: FusedContext) -> str:
        agri_data = context.agricultural_data
        yield_forecast = agri_data.get('yield_forecast', {})
        
        if yield_forecast:
            predicted_yield = yield_forecast.get('predicted_yield_kg_per_ha', 'N/A')
            confidence = yield_forecast.get('prediction_confidence', 'MEDIUM')
            
            response = f"Predicted crop yield: {predicted_yield} kg/ha (confidence: {confidence}). "
            
            recommendations = yield_forecast.get('recommendations', [])
            if recommendations:
                response += f"Recommendations: {', '.join(recommendations[:2])}"
            
            return response
        
        return "Yield predictions are being calculated based on current conditions."

    def _generate_crop_selection_response(self, context: FusedContext) -> str:
        agri_data = context.agricultural_data
        
        # Check for yield predictions
        yield_forecast = agri_data.get('yield_forecast', {})
        if yield_forecast:
            crop = yield_forecast.get('crop_type', 'recommended crop')
            yield_value = yield_forecast.get('predicted_yield_kg_per_ha')
            if yield_value:
                return f"Based on current conditions, {crop} is recommended with expected yield of {yield_value} kg/ha. Consider local soil conditions and market demand for final selection."
        
        # Check for semantic search results with crop information
        search_results = agri_data.get('search_results', [])
        if search_results:
            for result in search_results:
                text = result.get('document_text', '')
                if 'yield' in text.lower() or 'variety' in text.lower():
                    return f"For crop selection: {text[:200]}... Consider high-yielding varieties suited to your region."
        
        return "For optimal crop selection, consider your soil type, climate conditions, water availability, and local market demand. High-yielding varieties adapted to your region typically perform best."

    def _generate_scheme_response(self, context: FusedContext) -> str:
        gov_info = context.government_info
        schemes = gov_info.get('eligible_schemes', [])
        
        if schemes:
            scheme_names = [scheme.get('scheme_name', '') for scheme in schemes[:2]]
            response = f"You may be eligible for: {', '.join(scheme_names)}. "
            
            benefits = gov_info.get('financial_benefits', {})
            total_benefit = benefits.get('total_annual_benefit', 0)
            if total_benefit > 0:
                response += f"Potential annual benefit: ₹{total_benefit}"
            
            return response
        
        return "Government scheme eligibility is being checked based on your profile."

    def _generate_irrigation_response(self, context: FusedContext) -> str:
        weather = context.weather_intelligence
        irrigation_advice = weather.get('irrigation_recommendations', [])
        
        if irrigation_advice:
            return f"Irrigation guidance: {irrigation_advice[0]}"
        
        return "Irrigation recommendations are being prepared based on weather conditions."
    
    def _generate_fertilizer_response(self, context: FusedContext) -> str:
        agri_data = context.agricultural_data
        
        # Check for specific fertilizer recommendations from semantic search
        search_results = agri_data.get('search_results', [])
        for result in search_results:
            text = result.get('document_text', '')
            if any(word in text.lower() for word in ['fertilizer', 'npk', 'nitrogen', 'phosphorus', 'potash']):
                return f"Fertilizer recommendations: {text[:300]}..."
        
        # Default fertilizer advice
        return "For optimal fertilizer use, conduct soil testing to determine NPK requirements. Generally, apply nitrogen in split doses, phosphorus at sowing, and potash based on soil test results. Consider organic options like FYM for long-term soil health."
    
    def _generate_pest_response(self, context: FusedContext) -> str:
        agri_data = context.agricultural_data
        
        search_results = agri_data.get('search_results', [])
        for result in search_results:
            text = result.get('document_text', '')
            if any(word in text.lower() for word in ['pest', 'disease', 'insect', 'spray']):
                return f"Pest management guidance: {text[:300]}..."
        
        return "For effective pest management, monitor crops regularly, use integrated pest management (IPM) practices, and apply treatments based on economic threshold levels. Consult local agricultural extension services for specific pest identification."
    
    def _generate_soil_response(self, context: FusedContext) -> str:
        agri_data = context.agricultural_data
        
        search_results = agri_data.get('search_results', [])
        for result in search_results:
            text = result.get('document_text', '')
            if any(word in text.lower() for word in ['soil', 'ph', 'organic', 'health']):
                return f"Soil health recommendations: {text[:300]}..."
        
        return "Maintain soil health through regular organic matter addition, balanced fertilization, proper crop rotation, and avoiding over-tillage. Test soil pH and nutrient levels annually for optimal crop performance."

    # Helper methods for response components
    def _extract_weather_guidance(self, weather_intelligence: Dict) -> List[str]:
        advisories = weather_intelligence.get('agricultural_advisories', [])
        risks = weather_intelligence.get('risk_alerts', [])
        return advisories + risks

    def _extract_market_advice(self, market_intelligence: Dict) -> List[str]:
        recommendations = market_intelligence.get('trading_recommendations', [])
        return recommendations if recommendations else ['Monitor market trends closely']

    def _extract_agri_recommendations(self, agricultural_data: Dict) -> List[str]:
        productivity_advice = agricultural_data.get('productivity_advice', [])
        best_practices = agricultural_data.get('best_practices', [])
        return productivity_advice + best_practices

    def _extract_government_benefits(self, government_info: Dict) -> List[Dict]:
        return government_info.get('eligible_schemes', [])[:3]  # Top 3 schemes

    def _generate_action_items(self, classification: QueryClassification, context: FusedContext) -> List[str]:
        actions = []

        # Support dict contexts (enhanced_context) as well as FusedContext instances
        def g(ctx, key):
            if isinstance(ctx, dict):
                return ctx.get(key, {})
            return getattr(ctx, key, {})

        if classification.urgency == 'high':
            actions.append("⚡ Immediate action required - review recommendations carefully")

        if g(context, 'weather_intelligence').get('risk_alerts'):
            actions.append("🌤️ Check weather updates daily")

        if g(context, 'market_intelligence').get('current_prices'):
            actions.append("💰 Monitor market prices for optimal selling time")

        if g(context, 'government_info').get('eligible_schemes'):
            actions.append("🏛️ Apply for eligible government schemes")

        return actions if actions else ["📋 Review recommendations and plan accordingly"]

    def _interpret_confidence(self, confidence_score: float) -> str:
        if confidence_score > 0.8:
            return "HIGH - Recommendations based on comprehensive data"
        elif confidence_score > 0.6:
            return "MEDIUM - Good data coverage with some limitations"
        else:
            return "LOW - Limited data available, consult local experts"

    def _list_data_sources(self, tool_results: Dict) -> List[str]:
        sources = []
        for tool_name, result in tool_results.items():
            if result.success:
                source_map = {
                    'real_weather_apis': 'Live Weather Data',
                    'real_market_apis': 'Market Prices (AGMARKNET)',
                    'real_yield_prediction': 'ML Yield Models',
                    'government_apis': 'Government Schemes',
                    'sql_queries': 'Historical Agricultural Data',
                    'semantic_search': 'Agricultural Knowledge Base',
                    'google_search': 'Latest Web Information'
                }
                if tool_name in source_map:
                    sources.append(source_map[tool_name])
        return sources

    def _suggest_follow_ups(self, classification: QueryClassification) -> List[str]:
        follow_ups = {
            'weather_impact': [
                "How will this weather affect my specific crop?",
                "What irrigation adjustments should I make?",
                "Are there any pest risks with this weather?"
            ],
            'market_price_forecasting': [
                "When is the best time to sell my produce?",
                "What are the price trends for next month?",
                "Which market gives the best price?"
            ],
            'yield_prediction': [
                "How can I improve my expected yield?",
                "What fertilizers should I use?",
                "What are the best farming practices for my crop?"
            ]
        }
        
        return follow_ups.get(classification.primary_category, [
            "What other farming advice do you need?",
            "Would you like information about government schemes?",
            "Do you need market price updates?"
        ])

    def _generate_fallback_response(self, query: str) -> Dict[str, Any]:
        """Generate fallback response when processing fails"""
        return {
            'main_answer': "I'm experiencing some difficulty processing your agricultural query right now.",
            'recommendations': [
                "Please try rephrasing your question",
                "Contact your local agricultural extension office",
                "Check farmer.gov.in for immediate agricultural support"
            ],
            'confidence_level': "LOW - System error occurred"
        }

    def _update_performance_metrics(self, processing_time: float, tool_results: Dict):
        """Update system performance metrics"""
        # Update average processing time
        total = self.performance_metrics['total_queries']
        current_avg = self.performance_metrics['average_processing_time']
        new_avg = ((current_avg * (total - 1)) + processing_time) / total
        self.performance_metrics['average_processing_time'] = new_avg
        
        # Update tool usage stats
        for tool_name, result in tool_results.items():
            if tool_name not in self.performance_metrics['tool_usage_stats']:
                self.performance_metrics['tool_usage_stats'][tool_name] = {'used': 0, 'successful': 0}
            
            self.performance_metrics['tool_usage_stats'][tool_name]['used'] += 1
            if result.success:
                self.performance_metrics['tool_usage_stats'][tool_name]['successful'] += 1

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return self.performance_metrics.copy()

# Global RAG orchestrator instance
rag_orchestrator = AgriculturalRAGOrchestrator()

# Module-level function for easy import
async def process_agricultural_query(query: str, farmer_context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Module-level wrapper for processing agricultural queries
    
    Args:
        query: The farmer's question
        farmer_context: Optional context about the farmer's location, crops, etc.
    
    Returns:
        Dict containing the response and metadata
    """
    return await rag_orchestrator.process_farmer_query(query, farmer_context)
