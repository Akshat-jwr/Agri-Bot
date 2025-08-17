"""
Main RAG Orchestrator - Central Agricultural Intelligence Coordinator

File: app/tools/rag_core/rag_orchestrator.py
"""

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
        Main entry point for processing farmer queries
        Returns comprehensive agricultural intelligence response
        """
        start_time = datetime.now()
        self.performance_metrics['total_queries'] += 1
        
        logger.info(f"🌾 Processing farmer query: '{query[:50]}...'")
        
        try:
            # Step 1: Classify the query
            logger.info("🔍 Step 1: Classifying query...")
            classification = await query_classifier.classify_query(query, farmer_context)
            
            logger.info(f"✅ Classification: {classification.primary_category} "
                       f"(confidence: {classification.confidence:.2f})")
            
            # Step 2: Execute tools concurrently
            logger.info("🔧 Step 2: Executing tools concurrently...")
            tool_results = await tool_orchestrator.orchestrate_tools(classification, farmer_context)
            
            successful_tools = [name for name, result in tool_results.items() if result.success]
            logger.info(f"✅ Tool execution complete: {len(successful_tools)}/{len(tool_results)} successful")
            
            # Step 3: Fuse context from all tools
            logger.info("🔗 Step 3: Fusing context from all sources...")
            fused_context = await context_fusion.fuse_tool_results(tool_results, classification)
            
            # Step 4: Generate comprehensive response
            logger.info("📝 Step 4: Generating farmer response...")
            response = await self._generate_farmer_response(
                query, classification, fused_context, tool_results
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
                'classification': classification,
                'fused_context': fused_context,
                'processing_time': processing_time,
                'tools_used': list(tool_results.keys()),
                'confidence_score': fused_context.confidence_score
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Query processing failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'processing_time': processing_time,
                'fallback_response': self._generate_fallback_response(query)
            }

    async def _generate_farmer_response(self, 
                                      query: str,
                                      classification: QueryClassification,
                                      fused_context: FusedContext,
                                      tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive farmer-friendly response
        """
        # This is where you'd integrate with Gemini 2.5 Pro or another LLM
        # For now, we'll generate a structured response
        
        response = {
            'main_answer': await self._generate_main_answer(classification, fused_context),
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
        
        if classification.urgency == 'high':
            actions.append("⚡ Immediate action required - review recommendations carefully")
        
        if context.weather_intelligence.get('risk_alerts'):
            actions.append("🌤️ Check weather updates daily")
        
        if context.market_intelligence.get('current_prices'):
            actions.append("💰 Monitor market prices for optimal selling time")
        
        if context.government_info.get('eligible_schemes'):
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
